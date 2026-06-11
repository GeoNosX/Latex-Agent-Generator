from backend.schemas import ExamCuratorOutput
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# This is my LLM Config

llm = ChatOpenAI(
    model="meta/llama-3.1-70b-instruct", 
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1", temperature=0.2)

structured_curator = llm.with_structured_output(ExamCuratorOutput)


#for my latex_agent, this will be my llm

latex_llm = ChatOpenAI(
    model="meta/llama-3.1-70b-instruct", 
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1", temperature=0.0)