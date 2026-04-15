from graph.state import AgentState
from langchain_core.messages import AIMessage, SystemMessage
from llm.schemas import AgentAction
from local_mcp.client import mcp_operator
from llm.vllm_client import client
from config import settings
import json


async def llm_reasoning_node(state: AgentState):
    print("\n🧠 [Piko] Analyzing request...")

    # Give the LLM awareness of its tools
    available_tools = list(mcp_operator.tool_map.keys())

    system_prompt = f"""You are an autonomous Spaceship Piko. 
    Available tools: {available_tools}

    OPERATIONAL GUIDELINES:
    1. SUCCESS DETECTION: If a tool says "table already exists", that step is DONE. Move to the next task.
    2. TOOL SYNTAX: 
       - To write a file, you MUST provide 'path' and 'content'.
       - To run SQL, use 'write_query' with a 'query' string.
    3. INSTALL_SERVER is ONLY for tools that DO NOT EXIST in the list above. Never try to install 'sqlite' or 'filesystem' as they are already active.
    4. If you fail a task 3 times, use 'FINISH' and explain the blockage.

    Always output your response matching the AgentAction JSON schema."""

    oai_msgs = [{"role": "system", "content": system_prompt}]
    oai_msgs += [{"role": m.type if m.type in ["user", "assistant"] else "user", "content": m.content} for m in state["messages"]]

    try:
        # Force structured output via vLLM xgrammar
        response = await client.beta.chat.completions.parse(
            model=settings.VLLM_MODEL_NAME,
            messages=oai_msgs,
            response_format=AgentAction,
            temperature=0.1
        )
        action: AgentAction = response.choices[0].message.parsed
    except Exception as e:
        print(f"  ❌ LLM format error: {e}")
        action = AgentAction(thought="Fallback due to parsing error.", tool_name="FINISH", tool_arguments={})

    print(f"  💭 Thought: {action.thought}")
    print(f"  🛠️ Intended Action: {action.tool_name}")

    # Save the parsed action directly into the state for the next node
    return {"current_action": action}


async def tool_execution_node(state: AgentState):
    action: AgentAction = state.get("current_action")

    if action.tool_name == "FINISH":
        return {"task_completed": True, "needs_compilation": True}

    if action.tool_name == "INSTALL_SERVER":
        print(f"\n⚠️ [SECURITY INTERCEPT] The Piko wants to install a new server: {action.tool_arguments}")
        auth = input("Approve installation? (y/n): ")
        if auth.lower() == 'y':
            try:
                # Update servers.json
                with open("local_mcp/servers.json", "r+") as f:
                    config = json.load(f)
                    config[action.tool_arguments["server_name"]] = {
                        "command": action.tool_arguments["command"],
                        "args": action.tool_arguments["args"]
                    }
                    f.seek(0)
                    json.dump(config, f, indent=4)
                    f.truncate()
                result_text = "Server installed successfully. System requires reboot to load new tools."
            except Exception as e:
                result_text = f"Failed to modify servers.json: {str(e)}"
        else:
            result_text = "Installation rejected by Commander."
    else:
        # Real MCP Tool Execution
        try:
            raw_result = await mcp_operator.execute_tool(action.tool_name, action.tool_arguments)
            result_text = str(raw_result)
        except Exception as e:
            result_text = f"Tool execution failed: {str(e)}"

    print(f"  ✅ Result: {result_text[:100]}...")

    # Append the result to the LLM's context window so it knows what happened
    new_message = AIMessage(content=f"Tool '{action.tool_name}' returned: {result_text}")
    new_history = state.get("execution_history", "") + f"\nAction: {action.tool_name} | Args: {action.tool_arguments} | Result: {result_text}"

    return {
        "messages": [new_message],
        "execution_history": new_history
    }
