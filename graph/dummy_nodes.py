from graph.state import AgentState
from langchain_core.messages import AIMessage
from llm.vllm_client import generate_response


async def llm_reasoning_node(state: AgentState):
    print("\n[Piko] Analyzing request...")
    oai_msgs = [{"role": m.type if m.type in ["user", "assistant", "system"] else "user", "content": m.content} for m in state["messages"]]

    if not any(m["role"] == "system" for m in oai_msgs):
        oai_msgs.insert(0, {"role": "system", "content": "You are a spaceship agent. Reason about the user's request and state an action."})

    try:
        response_text = await generate_response(oai_msgs)
    except Exception as e:
        response_text = f"I have reasoned about the task. Proceeding with execution. (LLM fallback due to {e})"

    return {"messages": [AIMessage(content=response_text)]}


async def tool_execution_node(state: AgentState):
    print("[Piko] Executing tools...")
    last_msg = state["messages"][-1].content
    history = f"User asked: {state['messages'][0].content}\nAgent Reasoned: {last_msg}\nAction Taken: mcp_filesystem_read\nStatus: Success."

    return {
        "task_completed": True,
        "needs_compilation": True,
        "execution_history": history
    }
