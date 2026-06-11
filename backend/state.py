from typing import List, TypedDict, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    
    messages: List[BaseMessage]

    exercises: List[dict]

    latex_code: Optional[str]

    compiler_error: Optional[str]

    user_approved: Optional[bool]

