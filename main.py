import asyncio
import aiohttp
import sys
from memory.router import check_fast_path
from local_mcp.client import mcp_operator
from graph.main_workflow import app
from langchain_core.messages import HumanMessage
from config import settings


async def pre_flight_check():
    print("🔧 Running Pre-Flight Checks...")
    try:
        async with aiohttp.ClientSession() as session:
            # Check if Ollama is responsive
            async with session.get("http://localhost:11434/api/tags") as resp:
                if resp.status != 200:
                    raise Exception("Ollama heartbeat failed")
        print("  ✅ Ollama Engine: ONLINE")
    except Exception:
        print("\n❌ CRITICAL: Ollama is OFFLINE.")
        print("Please ensure the Ollama service is running on your machine.")
        sys.exit(1)

    await mcp_operator.initialize_servers()


async def main():
    await pre_flight_check()
    print("\n🚀 Spaceship Agent Ready. Awaiting commands.")
    try:
        while True:
            try:
                user_input = input("\nCommander: ")
            except (EOFError, KeyboardInterrupt):
                break

            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue

            # --- THE FAST PATH (Autopilot) ---
            fast_directive = check_fast_path(user_input)
            if fast_directive:
                print("⚡ [Autopilot] Executing compiled directive...")
                for step in fast_directive.get("steps", []):
                    result = await mcp_operator.execute_tool(step["action"], step["parameters"])
                    print(f"  Result: {str(result)[:200]}...")
                continue

            # --- THE SLOW PATH (Piko) ---
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "task_completed": False,
                "needs_compilation": False,
                "execution_history": f"Task: {user_input}\n"
            }

            # We must loop the LangGraph execution until 'task_completed' is true
            async for output in app.astream(initial_state):
                for node_name, state_update in output.items():
                    if node_name == "execute_tools" and state_update.get("task_completed"):
                        print("🎉 Task Accomplished.")
    finally:
        # --- FIX: Ensure MCP servers are closed before exiting ---
        await mcp_operator.shutdown()
if __name__ == "__main__":
    asyncio.run(main())
