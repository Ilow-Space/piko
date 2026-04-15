from graph.state import AgentState
from llm.vllm_client import compile_directive
from memory.lancedb_store import save_directive_to_disk
from memory.router import add_new_route
from llm.schemas import CompiledDirective, RAGStep
import asyncio


async def background_compiler_node(state: AgentState):
    if state.get("needs_compilation") and state.get("task_completed"):
        print("\n[Background] Piko is compiling new RAG directive...")

        try:
            # 1. Ask vLLM to write the JSON directive based on what just happened
            directive = await compile_directive(state["execution_history"])
        except Exception as e:
            print(f"[Background] vLLM compile failed: {e}. Generating fallback directive.")
            directive = CompiledDirective(
                intent_description="Fallback mock task directive",
                trigger_phrases=[state["messages"][0].content, "do mock task", "run routine"],
                steps=[RAGStep(action="mcp_mock_tool", parameters={"target": "system"})]
            )

        # 2. Save it to disk
        safe_name = directive.intent_description.replace(" ", "_").lower()[:30]
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")

        save_directive_to_disk(directive.model_dump(), safe_name)

        # 3. Update the semantic router immediately
        add_new_route(safe_name, directive.trigger_phrases)

        print(f"[Background] Compilation complete. Route '{safe_name}' added to Autopilot.")

    return state
