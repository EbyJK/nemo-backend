from fastapi import APIRouter
from app.schemas.email import EmailInput
from pydantic import BaseModel

router = APIRouter()

class SummaryOutput(BaseModel):
    summary: str

@router.post("/", response_model=SummaryOutput)
def summarize_email(email: EmailInput):
    return {
        "summary": "This is a dummy summary of the email content."
    }
