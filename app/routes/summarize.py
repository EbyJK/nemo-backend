from fastapi import APIRouter
from app.schemas.email import EmailInput
from pydantic import BaseModel
from datetime import datetime
router = APIRouter()

class SummaryOutput(BaseModel):
    summary: str

# @router.post("/", response_model=SummaryOutput)
# def summarize_email(email: EmailInput):
#     return {
#         "summary": "This is a dummy summary of the email content."
#     }
@router.post("/", response_model=SummaryOutput)
def summarize_email(email: EmailInput):
    return {
        "summary": (
            "Finance team has requested submission of the Q4 budget report "
            "by January 5 EOD. Timely submission is required to avoid delays "
            "in approval."
        )
    }

@router.get("/summaries")
def get_summaries():
    """
    Dummy summaries.
    Final structure — content will be replaced by ML.
    """

    summaries = [
        {
            "summary": (
                "Finance team has requested submission of the Q4 budget report "
                "by January 5 EOD. Timely submission is required to avoid delays "
                "in approval."
            ),
            "confidence": 0.92
        },
        {
            "summary": (
                "A client review meeting with ABC Corp has been scheduled "
                "for January 10 at 3 PM. Key discussion points include project "
                "progress and next deliverables."
            ),
            "confidence": 0.89
        }
    ]

    return summaries