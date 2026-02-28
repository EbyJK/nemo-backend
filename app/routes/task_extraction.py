# from fastapi import APIRouter
# from app.ml.task_extractor_model import extract_tasks_from_text
# from app.schemas.email import EmailInput
# import json

# router = APIRouter()

# @router.post("/extract-tasks")
# def extract_tasks_api(email: EmailInput):
#     text = email.subject + " " + email.body
#     raw_output = extract_tasks_from_text(text)

#     try:
#         tasks = json.loads(raw_output)
#     except:
#         tasks = [{"title": raw_output, "priority": "medium"}]

#     return {"tasks": tasks}