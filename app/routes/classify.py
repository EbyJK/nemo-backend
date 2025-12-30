from fastapi import APIRouter
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationOutput

router = APIRouter()

@router.post("/", response_model=ClassificationOutput)
def classify_email(email: EmailInput):
    return {
        "is_corporate": True,
        "confidence": 0.95,
        "category": "meeting"
    }
