from fastapi import APIRouter
from app.schemas.email import EmailInput
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Task(BaseModel):
    title: str
    due_date: Optional[str] = None
    priority: str

class TaskListOutput(BaseModel):
    tasks: List[Task]

@router.post("/extract", response_model=TaskListOutput)
def extract_tasks(email: EmailInput):
    return {
        "tasks": [
            {
                "title": "Attend meeting",
                "due_date": "2025-01-05",
                "priority": "high"
            }
        ]
    }
