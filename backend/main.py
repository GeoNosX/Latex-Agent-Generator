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