from fastapi import APIRouter
from app.schemas.email import EmailInput
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
router = APIRouter()

class Task(BaseModel):
    title: str
    due_date: Optional[str] = None
    priority: str

class TaskListOutput(BaseModel):
    tasks: List[Task]

# @router.post("/extract", response_model=TaskListOutput)
# def extract_tasks(email: EmailInput):
#     return {
#         "tasks": [
#             {
#                 "title": "Attend meeting",
#                 "due_date": "2025-01-05",
#                 "priority": "high"
#             }
#         ]
#     }

@router.post("/extract", response_model=TaskListOutput)
def extract_tasks(email: EmailInput):
    return {
        "tasks": [
            {
                "title": "Submit Q4 budget report",
                "due_date": "2026-01-05T17:00:00",
                "priority": "high"
            }
        ]
    }



@router.get("/tasks")
def get_tasks(completed: bool = False):
    """
    Dummy corporate-grade tasks.
    This shape is FINAL and ML will later replace values.
    """

    tasks = [
        {
            "title": "Submit Q4 budget report",
            "due_date": "2026-01-05T17:00:00",
            "priority": "high",
            "context": "Requested by Finance team via corporate email",
            "source_sentence": "Please submit the Q4 budget report by Jan 5 EOD",
            "completed": False
        },
        {
            "title": "Client review meeting with ABC Corp",
            "due_date": "2026-01-10T15:00:00",
            "priority": "high",
            "context": "Meeting scheduled with external client",
            "source_sentence": "Let's have a review call on Jan 10 at 3 PM",
            "completed": False
        }
    ]

    return tasks