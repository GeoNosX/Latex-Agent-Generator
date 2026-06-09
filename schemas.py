from pydantic import BaseModel, Field
from typing import List

class Exercise(BaseModel):
    id: int = Field(description="A unique sequential index starting at 1.")
    instruction: str = Field(description="The prompt or command for the student. e.g., 'Solve for x:', 'Calculate the determinant:'")
    content: str = Field(description="The mathematical body of the question, using standard text format.")
    difficulty: str = Field(description="Easy, Medium, or Hard.")

class ExamCuratorOutput(BaseModel):
    title: str = Field(description="The title of the worksheet or exam.")
    exercises: List[Exercise] = Field(description="The list of curated math exercises.")