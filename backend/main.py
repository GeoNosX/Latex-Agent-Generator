from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage

from graph import app as graph_app

app = FastAPI(title="LaTeX Math Agent API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str
    thread_id: str

class ResumeRequest(BaseModel):
    thread_id: str
    exercises: List[dict]
    user_approved: bool

@app.post('/api/generate')
async def generate_exam(request :GenerateRequest):

    """Initializes a thread and runs the graph until the human review roadblock."""

    config = {"configurable": {"thread_id": request.thread_id}}
    initial_state = {
        "messages": [HumanMessage(content=request.prompt)],
        "exercises": [],
        "latex_code": None,
        "compiler_error": None,
        "user_approved": False
    }

    try:
        graph_app.invoke(initial_state,config=config)
        current_state = graph_app.get_state(config)
        return {
            "status": "paused_for_review",
            "thread_id": request.thread_id,
            "exercises": current_state.values.get("exercises", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get('/api/status/{thread_id}')
async def get_status(thread_id: str):

    """Fetches the complete data state for an active session."""

    config = {"configurable": {"thread_id": thread_id}}
    current_state = graph_app.get_state(config)

    if not current_state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return {
        "exercises": current_state.values.get("exercises", []),
        "latex_code": current_state.values.get("latex_code"),
        "compiler_error": current_state.values.get("compiler_error"),
        "next_step": current_state.next  # Tells us if the graph is currently interrupted
    }

@app.post('/api/resume')
async def resume_graph (request: ResumeRequest):
    """Overwrites state with human updates and signals the graph to continue."""
    config = {"configurable": {"thread_id": request.thread_id}}

    graph_app.update_state(config, 
                           
                           {'exercises': request.exercises,
                            'user_approved': request.user_approved})

    try:
        graph_app.invoke(None, config=config)
        final_state = graph_app.get_state(config)


        if "human_review" in final_state.next:
            return {
                "status": "paused_for_review",
                "exercises": final_state.values.get("exercises", []),
                "message": "Exercises adjusted based on your feedback. Ready for another look."
            }
        return {
                "status": "completed",
                "latex_code": final_state.values.get("latex_code"),
                "compiler_error": final_state.values.get("compiler_error")
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resuming failed: {str(e)}")


    
    