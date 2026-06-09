from langgraph.graph import StateGraph, END
from state import AgentState
from langgraph.checkpoint.memory import MemorySaver


def curator_agent(state: AgentState) -> str:
    print("--- CURATING EXERCISES ---")

    return {"exercises": state.get("exercises", [])}

def human_review_node(state: AgentState) -> str:
    print("--- WAITING FOR USER APPROVAL ---")

    return{}

def latex_generator_agent(state:AgentState):
    print("--- GENERATING LATEX ---")

    return {"latex_code": " % LaTeX content goes here"} 

def compiler_node(state:AgentState):
    print("--- COMPILING LATEX ---")

    success = True  # Simulate compilation success
    if success:
        return {"compiler_error": None}
    else:
        return {"compiler_error": "Compilation failed due to syntax errors."}
    

workflow = StateGraph(AgentState)

workflow.add_node("curator", curator_agent)
workflow.add_node("human_review", human_review_node)
workflow.add_node("latex_generator", latex_generator_agent)
workflow.add_node("compiler", compiler_node)

workflow.set_entry_point("curator")

workflow.add_edge("curator", "human_review")

def route_after_human_review(state: AgentState) -> str:
    if state.get("user_approved"):
        return "latex_generator"
    return "curator"


workflow.add_edge("human_review", 
                  route_after_human_review,{
        "latex_generator": "latex_generator",
        "curator": "curator"})

workflow.add_edge("latex_generator", "compiler")

def route_after_compilation(state: AgentState):
    if state.get("compiler_error"):
        return "latex_generator"
    return END  

workflow.add_conditional_edges(
    "compiler",
    route_after_compilation,
    {
        "latex_generator": "latex_generator",
        "end": END
    }
)


memory=MemorySaver()
app=workflow.compile(checkpointer=memory, interrupt_before=["human_review"])