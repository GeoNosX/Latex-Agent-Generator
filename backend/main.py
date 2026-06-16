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
    
    