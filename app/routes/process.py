from fastapi import APIRouter
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationOutput
from app.routes.classify import classify_email
from app.routes.summarize import summarize_email
from app.routes.tasks import extract_tasks

router = APIRouter()

@router.post("/")
def process_email(email: EmailInput):
    classification = classify_email(email)

    if not classification["is_corporate"]:
        return {
            "is_corporate": False,
            "message": "Non-corporate email ignored"
        }

    summary = summarize_email(email)
    tasks = extract_tasks(email)

    return {
        "is_corporate": True,
        "classification": classification,
        "summary": summary,
        "tasks": tasks
    }
