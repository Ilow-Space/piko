from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.compiler_node import background_compiler_node
from graph.nodes import llm_reasoning_node, tool_execution_node

def should_compile(state: AgentState):
    if state.get("task_completed") and state.get("needs_compilation"):
        return "compiler"
    elif not state.get("task_completed"):
        # Loop back to continue ReAct processing if not FINISH
        return "reason"
    return END

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("reason", llm_reasoning_node)
workflow.add_node("execute_tools", tool_execution_node)
workflow.add_node("compiler", background_compiler_node)

# Define Edges (The Flow)
workflow.set_entry_point("reason")
workflow.add_edge("reason", "execute_tools")

# Conditional routing: If task is done, trigger compiler. If not, go back to reason.
workflow.add_conditional_edges("execute_tools", should_compile, {
    "reason": "reason",
    "compiler": "compiler",
    END: END
})
workflow.add_edge("compiler", END)

app = workflow.compile()
