# from fastapi import APIRouter
# from app.schemas.email import EmailInput
# from pydantic import BaseModel
# from datetime import datetime
# router = APIRouter()

# class SummaryOutput(BaseModel):
#     summary: str

# # @router.post("/", response_model=SummaryOutput)
# # def summarize_email(email: EmailInput):
# #     return {
# #         "summary": "This is a dummy summary of the email content."
# #     }
# @router.post("/", response_model=SummaryOutput)
# def summarize_email(email: EmailInput):
#     return {
#         "summary": (
#             "Finance team has requested submission of the Q4 budget report "
#             "by January 5 EOD. Timely submission is required to avoid delays "
#             "in approval."
#         )
#     }

# @router.get("/summaries")
# def get_summaries():
#     """
#     Dummy summaries.
#     Final structure — content will be replaced by ML.
#     """

#     summaries = [
#         {
#             "summary": (
#                 "Finance team has requested submission of the Q4 budget report "
#                 "by January 5 EOD. Timely submission is required to avoid delays "
#                 "in approval."
#             ),
#             "confidence": 0.92
#         },
#         {
#             "summary": (
#                 "A client review meeting with ABC Corp has been scheduled "
#                 "for January 10 at 3 PM. Key discussion points include project "
#                 "progress and next deliverables."
#             ),
#             "confidence": 0.89
#         }
#     ]

#     return summaries



from fastapi import APIRouter
from app.schemas.email import EmailInput
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os


router = APIRouter()

class SummaryOutput(BaseModel):
    summary: str

# 🔹 Load model ONLY once when server starts
MODEL_PATH = "app/ml/t5_summarizer"   # ⚠️ change if your folder name is different

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
    model.eval()
    print("✅ Summarizer model loaded successfully.")
except Exception as e:
    print("❌ Error loading summarizer model:", e)
    tokenizer = None
    model = None


@router.post("/", response_model=SummaryOutput)
def summarize_email(email: EmailInput):

    # 🔹 If model not loaded → fallback dummy summary
    if tokenizer is None or model is None:
        return {
            "summary": "Model not loaded. Dummy summary returned."
        }

    try:
        input_text = "summarize: " + email.subject + " " + email.body

        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=150,
                num_beams=4,
                early_stopping=True
            )

        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "summary": summary
        }

    except Exception as e:
        print("❌ Summarization error:", e)
        return {
            "summary": "Error during summarization. Dummy fallback."
        }

def generate_summary(subject: str, body: str) -> str:
    text = "summarize: " + subject + " " + body

    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_length=60,
            num_beams=2,
            early_stopping=True,
             output_scores=True,
            return_dict_in_generate=True
        )

    # summary = tokenizer.decode(output[0], skip_special_tokens=True)
    summary_ids = output.sequences[0]
    summary = tokenizer.decode(summary_ids, skip_special_tokens=True)
    confidence=0.5  # default confidence
    try:
    # 🔹 Compute confidence from token probabilities
        scores = output.scores  # list of logits
        token_probs = []

    # for i, score in enumerate(scores):
    #     probs = torch.softmax(score, dim=-1)
    #     token_id = summary_ids[i + 1]  # shift because first token is start token
    #     token_prob = probs[0, token_id]
    #     token_probs.append(token_prob.item())
    
    
    # FIX: iterate only over valid range
        for i in range(min(len(scores), len(summary_ids) - 1)):
            probs = torch.softmax(scores[i], dim=-1)
            token_id = summary_ids[i + 1]  # safe now
            token_prob = probs[0, token_id]
            token_probs.append(token_prob.item())
    
    

        if token_probs:
            confidence = sum(token_probs) / len(token_probs)
        # else:
        #     confidence = 0.5
    except Exception as e:
        print("Confidence calculation failed:", e)
           

    return summary, round(confidence, 2)
    
