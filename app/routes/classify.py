# from fastapi import APIRouter
# from app.schemas.email import EmailInput
# from app.schemas.classification import ClassificationOutput

# router = APIRouter()

# @router.post("/", response_model=ClassificationOutput)
# def classify_email(email: EmailInput):
#     return {
#         "is_corporate": True,
#         "confidence": 0.95,
#         "category": "meeting"
#     }


from fastapi import APIRouter
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationOutput
from app.ml.classifier import classify_text, classify_proba

router = APIRouter()

@router.post("/", response_model=ClassificationOutput)
def classify_email(email: EmailInput):
    # Combine subject + body into a single text
    full_text = f"{email.subject} {email.body}"

    # Get prediction and confidence
    label, confidence = classify_proba(full_text)

    # Convert label to schema fields
    is_corporate = True if label == "Corporate" else False

    return {
        "is_corporate": is_corporate,
        "confidence": confidence,
        "category": label.lower()   # corporate / non_corporate
    }
