from prompts import CURATOR_PROMPT, LATEX_PROMPT
from langgraph.graph import StateGraph, END
from state import AgentState
from langgraph.checkpoint.memory import MemorySaver
from schemas import ExamCuratorOutput

from langchain_core.prompts import ChatPromptTemplate
from llms import structured_curator, latex_llm



def curator_agent(state: AgentState) -> str:
    print("--- CURATING EXERCISES ---")
    messages=state['messages']
    current_exercises = state.get("exercises", [])
    prompt = ChatPromptTemplate.from_messages([
        ("system", CURATOR_PROMPT),
        *messages      

    ])
    chain = prompt | structured_curator
    response = chain.invoke({"current_exercises": current_exercises})


    return {"exercises": [ex.model_dump() for ex in response.exercises],
        "messages": messages}





def human_review_node(state: AgentState) -> str:
    print("--- WAITING FOR USER APPROVAL ---")

    return{}





def latex_generator_agent(state:AgentState):
    print("--- GENERATING LATEX CODE---")
    exerscises = state.get("exercises", [])
    compiler_error= state.get("compiler_error", 'None')
    prompt = ChatPromptTemplate.from_messages([
        ("system", LATEX_PROMPT),
        ('human', 'Generate LaTeX code for the following exercises:'),
    ])

    chain = prompt | latex_llm
    response = chain.invoke({"exercises": exerscises, "compiler_error": compiler_error})

    return {"latex_code": response.latex_code,
            "compiler_error": None}
 






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