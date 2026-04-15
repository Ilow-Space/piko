from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RAGStep(BaseModel):
    action: str = Field(description="The MCP tool or internal function to call, e.g., 'mcp_filesystem_read'")
    parameters: Dict[str, Any] = Field(description="Arguments for the action")

class CompiledDirective(BaseModel):
    intent_description: str = Field(description="A clear description of what this directive solves")
    trigger_phrases: List[str] = Field(description="5 example phrases that should trigger this pipeline")
    steps: List[RAGStep] = Field(description="The deterministic pipeline of steps to execute")

class AgentAction(BaseModel):
    thought: str = Field(description="Your step-by-step reasoning about what to do next.")
    tool_name: str = Field(description="The exact name of the tool to execute. Use 'FINISH' if the user's task is fully complete.")
    tool_arguments: Dict[str, Any] = Field(default_factory=dict, description="A JSON object containing the arguments for the tool.")
    
class SystemToolInstaller(BaseModel):
    server_name: str = Field(description="A descriptive name for the server (e.g., 'github', 'telegram')")
    command: str = Field(description="The executor command, usually 'npx' or 'uvx'")
    args: List[str] = Field(description="The list of arguments, including the package name and flags")
