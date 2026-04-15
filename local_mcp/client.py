import json
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack


class MCPOperator:
    def __init__(self):
        self.sessions = {}
        self.tool_map = {}  # Maps tool_name -> server_name
        self.exit_stack = AsyncExitStack()

    async def initialize_servers(self):
        print("[System] Booting MCP Servers...")

        # Ensure the file exists
        if not os.path.exists("local_mcp/servers.json"):
            os.makedirs("local_mcp", exist_ok=True)
            with open("local_mcp/servers.json", "w") as f:
                f.write("{}")

        with open("local_mcp/servers.json", "r") as f:
            servers = json.load(f)

        for name, config in servers.items():
            try:
                server_params = StdioServerParameters(
                    command=config["command"],
                    args=config["args"],
                    env=config.get("env", None)
                )
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                self.sessions[name] = session

                # Ask the server what tools it has and map them
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    self.tool_map[tool.name] = name

                print(f"  ✅ {name} online (Available tools: {len(tools_response.tools)})")
            except Exception as e:
                print(f"  ❌ Failed to load {name}: {e}")

    async def execute_tool(self, tool_name: str, arguments: dict):
        if tool_name not in self.tool_map:
            raise ValueError(f"Tool '{tool_name}' not found in any active MCP server.")

        server_name = self.tool_map[tool_name]
        session = self.sessions[server_name]

        result = await session.call_tool(tool_name, arguments)

        # Ensure we return a string representation of the result content
        if hasattr(result, "content") and isinstance(result.content, list):
            return "\n".join(str(c) for c in result.content)
        return str(result)

    async def shutdown(self):
        print("[System] Closing MCP connections...")
        await self.exit_stack.aclose()


# Global instance
mcp_operator = MCPOperator()
