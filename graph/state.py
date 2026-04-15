from typing import TypedDict, Annotated, Optional, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task_completed: bool
    needs_compilation: bool
    execution_history: str
    current_action: Optional[Any]
