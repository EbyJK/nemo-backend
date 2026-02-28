# from fastapi import APIRouter
# from app.schemas.email import EmailInput
# from pydantic import BaseModel
# from typing import List, Optional
# from datetime import datetime

# from app.ml.task_extractor.task_extractor import extract_tasks as ml_extract

# router = APIRouter()

# class Task(BaseModel):
#     title: str
#     due_date: Optional[str] = None
#     priority: str

# class TaskListOutput(BaseModel):
#     tasks: List[Task]

# def clean_title(description: str) -> str:
#     """
#     Option B — Clean polite/leading words.
#     Removes words like 'please', 'kindly', 'could you', etc.
#     """
#     desc = description.strip()

#     # lowercase copy for detection
#     d = desc.lower()

#     polite_prefixes = [
#         "please ", "kindly ", "can you ", "could you ",
#         "i request you to ", "i request you ", "pls ",
#         "please do ", "please make sure to "
#     ]

#     for p in polite_prefixes:
#         if d.startswith(p):
#             desc = desc[len(p):]

#     # Capitalize first letter
#     if len(desc) > 0:
#         desc = desc[0].upper() + desc[1:]

#     return desc


# def extract_tail_sentences(body: str, count: int = 2) -> str:
#     """Extract last 1–2 meaningful sentences from email body."""
#     parts = [s.strip() for s in body.split('.') if s.strip()]
#     if not parts:
#         return ""
#     return ". ".join(parts[-count:])

# @router.post("/extract", response_model=TaskListOutput)
# def extract_tasks(email: EmailInput):
    

#     """
#     ML-based task extraction using:
#     - summary (if provided)
#     - OR subject+body fallback
#     - last 2 sentences of body
#     - real ML task model
#     """
#     from app.ml.task_extractor.task_extractor import extract_tasks as ml_extract

#     # 1) Extract summary if available (without changing summarizer code)
#     summary_text = ""
#     if hasattr(email, "summary") and email.summary:
#         if isinstance(email.summary, dict):
#             summary_text = email.summary.get("summary", "")
#         elif isinstance(email.summary, tuple):
#             summary_text = email.summary[0]
#         else:
#             summary_text = str(email.summary)
#     else:
#         summary_text = f"{email.body}"

#     # 2) Extract last 2 sentences of body
#     def extract_tail(body):
#         parts = [s.strip() for s in body.split('.') if s.strip()]
#         return ". ".join(parts[-2:]) if parts else ""

#     tail_text = extract_tail(email.body)

#     # 3) Combine (Option B)
#     combined_text = summary_text + ". " + tail_text

#     # 4) Run ML extractor
#     raw_tasks = ml_extract(combined_text)

#     # 5) Clean title and remove subject contamination
#     def clean_title(description: str) -> str:
#         desc = description.strip()
#         # remove subject if prefixed
#         if email.subject.lower() in desc.lower():
#             desc = desc.replace(email.subject, "", 1).strip()

#         # polite prefixes
#         prefixes = [
#             "please ", "kindly ", "can you ", "could you ", "pls ",
#             "i request you to ", "please do "
#         ]
#         dl = desc.lower()
#         for p in prefixes:
#             if dl.startswith(p):
#                 desc = desc[len(p):]
#                 break

#         # Capitalize
#         if desc:
#             desc = desc[0].upper() + desc[1:]
#         return desc

#     # 6) Convert and remove duplicates
#     unique = {}
#     for t in raw_tasks:
#         title = clean_title(t.get("description", ""))

#         if not title:
#             continue
        
        
#         if title not in unique:
#             unique[title] = {
#                 "title": title,
#                 "due_date": t.get("due_date"),
#                 "priority": t.get("priority", "medium").lower()
#             }

#     return {"tasks": list(unique.values())}








# # @router.post("/extract", response_model=TaskListOutput)
# # def extract_tasks(email: EmailInput):
# #     return {
# #         "tasks": [
# #             {
# #                 "title": "Submit Q4 budget report",
# #                 "due_date": "2026-01-05T17:00:00",
# #                 "priority": "high"
# #             }
# #         ]
# #     }






from fastapi import APIRouter
from app.schemas.email import EmailInput
from pydantic import BaseModel
from typing import List, Optional

from app.ml.task_extractor.task_extractor import extract_tasks as ml_extract

router = APIRouter()

class Task(BaseModel):
    title: str
    due_date: Optional[str] = None
    priority: str

class TaskListOutput(BaseModel):
    tasks: List[Task]


# ------------------------------------------------------------
# CLEAN TITLE (Option B) - Remove polite words & fix casing
# ------------------------------------------------------------
def clean_title(description: str, subject: str = "") -> str:
    desc = description.strip()

    # Remove subject if it appears inside
    if subject and subject.lower() in desc.lower():
        desc = desc.replace(subject, "", 1).strip()

    # Polite prefixes to remove
    polite_prefixes = [
        "please ", "kindly ", "can you ", "could you ",
        "i request you to ", "i request you ", "pls ",
        "please do ", "please make sure to "
    ]

    d = desc.lower()
    for p in polite_prefixes:
        if d.startswith(p):
            desc = desc[len(p):]
            break

    # Capitalize first character
    if desc:
        desc = desc[0].upper() + desc[1:]

    return desc.strip()


# ------------------------------------------------------------
# TAIL SENTENCES EXTRACTION (Option B)
# ------------------------------------------------------------
def extract_tail_sentences(body: str, count: int = 2) -> str:
    parts = [s.strip() for s in body.split('.') if s.strip()]
    if not parts:
        return ""
    return ". ".join(parts[-count:])


# ------------------------------------------------------------
# GARBAGE TASK FILTER  (NEW)
# ------------------------------------------------------------
def is_garbage(title: str) -> bool:
    """
    Filters out marketing/garbage tasks generated from promotional
    or tracking-heavy emails (LinkedIn, newsletters, ads, etc.)
    """

    t = title.lower()

    # URL / tracking detection
    if "http://" in t or "https://" in t:
        return True
    if "utm_" in t or "trk=" in t or "tracking" in t:
        return True

    # Common marketing / promotional noise
    garbage_phrases = [
        "unsubscribe", "premium", "help:", "learn why",
        "profile views", "view profile", "notification",
        "upgrade", "unlock", "get more", "see more",
        "your profile is looking great"
    ]
    for phrase in garbage_phrases:
        if phrase in t:
            return True

    # Long sentences are rarely real tasks
    if len(t) > 120:
        return True

    # Must contain at least one actionable verb
    verbs = [
        "submit", "prepare", "schedule", "review", "complete",
        "finish", "update", "send", "call", "meet", "finalize",
        "draft", "attach", "upload"
    ]
    if not any(v in t for v in verbs):
        return True

    return False


# ------------------------------------------------------------
# MAIN TASK EXTRACTOR ENDPOINT
# ------------------------------------------------------------
@router.post("/extract", response_model=TaskListOutput)
def extract_tasks(email: EmailInput):
    """
    ML-based task extraction:
    - summary (if provided)
    - OR body fallback
    - last 2 sentences (Option B)
    - filtered for garbage tasks
    """

    # 1) Summary extraction
    summary_text = ""
    if hasattr(email, "summary") and email.summary:
        if isinstance(email.summary, dict):
            summary_text = email.summary.get("summary", "")
        elif isinstance(email.summary, tuple):
            summary_text = email.summary[0]
        else:
            summary_text = str(email.summary)
    else:
        summary_text = email.body

    # 2) Extract last 2 sentences from body (Option B)
    tail_text = extract_tail_sentences(email.body, count=2)

    # 3) Combine summary + tail
    combined_text = f"{summary_text}. {tail_text}"

    # 4) Run ML extraction
    raw_tasks = ml_extract(combined_text)

    # 5) Convert, clean, dedupe, filter garbage
    unique = {}

    for t in raw_tasks:
        raw_desc = t.get("description", "")
        title = clean_title(raw_desc, subject=email.subject)

        if not title:
            continue

        #  Skip marketing/garbage tasks
        if is_garbage(title):
            continue

        #  Deduplicate based on title
        if title not in unique:
            unique[title] = {
                "title": title,
                "due_date": t.get("due_date"),
                "priority": t.get("priority", "medium").lower()
            }

    return {"tasks": list(unique.values())}
























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