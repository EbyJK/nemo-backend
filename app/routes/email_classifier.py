from fastapi import APIRouter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.routes.calendar import TOKEN_STORE, CLIENT_ID, CLIENT_SECRET
from app.ml.classifier import classify_proba
from app.ml.category_classifier import detect_category
import base64
from app.core.db import insert_email, insert_summary, insert_tasks
from app.routes.summarize import summarize_email
from app.routes.tasks import extract_tasks
from app.core.supabase import supabase
from app.schemas.email import EmailInput
from app.routes.summarize import generate_summary
# from app.routes.tasks_extraction import extract_tasks_api
from app.routes.tasks import extract_tasks as extract_tasks_backend


router = APIRouter()
def email_exists(gmail_id: str):
    result = supabase.table("emails") \
        .select("id") \
        .eq("gmail_id", gmail_id) \
        .execute()
    
    return len(result.data) > 0


# def decode_email_body(msg):
#     if msg.get("parts"):
#         for part in msg["parts"]:
#             try:
#                 data = part["body"]["data"]
#                 return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
#             except:
#                 continue
#     try:
#         data = msg["body"]["data"]
#         return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
#     except:
#         return ""
def decode_email_body(payload):
    body = ""

    if "parts" in payload:
        for part in payload["parts"]:
            # Look for text/plain part
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    return body

            # Sometimes nested parts
            if "parts" in part:
                for subpart in part["parts"]:
                    if subpart.get("mimeType") == "text/plain":
                        data = subpart["body"].get("data")
                        if data:
                            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                            return body

    # fallback (single-part email)
    if payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return body

    
    
def check_attachment(payload):
    if payload.get("parts"):
        for part in payload["parts"]:
            if part.get("filename"):
                return True
    return False

def extract_attachments(payload):
    attachments = []

    parts = payload.get("parts", [])
    for part in parts:
        filename = part.get("filename")
        if filename:
            mime_type = part.get("mimeType", "")
            attachments.append({
                "filename": filename,
                "type": mime_type
            })

    return attachments


@router.get("/emails/classified")

def classified_emails():
    if "access_token" not in TOKEN_STORE:
        return {"error": "User not authenticated"}

    creds = Credentials(
        token=TOKEN_STORE["access_token"],
        refresh_token=TOKEN_STORE["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    service = build("gmail", "v1", credentials=creds)

    result = service.users().messages().list(
        userId="me",
        maxResults=20,
        q="is:unread"
    ).execute()

    messages = result.get("messages", [])
    output = []

    for m in messages:

        # Skip duplicates
        if email_exists(m["id"]):
            continue

        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="full"
        ).execute()

        headers = msg["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")
        body = decode_email_body(msg["payload"])
        has_attachment = check_attachment(msg["payload"])
        attachments = extract_attachments(msg["payload"])
        has_attachment = len(attachments) > 0

        email_text = subject + " " + body

        # 1️⃣ Corporate classifier
        label, confidence = classify_proba(email_text)

        # if label.lower() != "corporate":
        #     continue

        is_corporate = (label.lower() == "corporate")
        print("DEBUG: email_classifier.py -> classify_emails() is running")
# ------------------------------------------------------
# BUSINESS KEYWORD OVERRIDE 
# ------------------------------------------------------
        business_keywords = [
            "project", "status", "update", "action", "required",
            "review", "deliverable", "deadline", "schedule",
            "submit", "report", "documentation", "meeting", "team"
        ]

        subject_lower = subject.lower()
        body_lower = body.lower()

        if any(keyword in subject_lower for keyword in business_keywords):
            is_corporate = True

        # If still not corporate → skip
        if not is_corporate:
            continue
        # ------------------------------------------------------
        
        
        attachment_types = [att["type"] for att in attachments]             
        # 2️⃣ Insert email into DB
        email_row = insert_email({
            "gmail_id": m["id"],
            "subject": subject,
            "sender": sender,
            "body": body,
            "is_corporate": True,
            "confidence": confidence,
            "category": detect_category(email_text),
            "has_attachment": has_attachment,
            "attachment_count": len(attachments),
            "attachment_types":attachment_types,
            "attachments": attachments,
            "user_id": None
        })

        # 3️⃣ Summarize
        # summary_output = summarize_email(
        #     EmailInput(subject=subject, body=body, sender=sender)
        # )
        from app.routes.summarize import generate_summary
        summary_text,summary_confidence = generate_summary(subject, body)

        insert_summary({
         "email_id": email_row["id"],
        "summary": summary_text,
        "confidence": summary_confidence
        })

        # insert_summary({
        #     "email_id": email_row["id"],
        #     "summary": summary_output["summary"]
        # })




        # 4️⃣ Extract tasks
        
        # tasks_output = extract_tasks_api(
        #     EmailInput(subject=subject, body=body, sender=sender)
        # )

        # task_rows = []
        # for t in tasks_output["tasks"]:
        #     task_rows.append({
        #         "email_id": email_row["id"],
        #         "title": t.get("title"),
        #         "priority": t.get("priority", "medium"),
        #         "due_date": t.get("due_date")   # if model returns
        #     })
    
        # if task_rows:
        #     insert_tasks(task_rows)
        
        
        
        
        tasks_output = extract_tasks(
            EmailInput(subject=subject, body=body, sender=sender,summary=summary_text)
        )

        task_rows = []
        for task in tasks_output["tasks"]:
            task_rows.append({
                "email_id": email_row["id"],
                "title": task["title"],
                "due_date": task.get("due_date"),
                "priority": task["priority"]
            })

        if task_rows:
            insert_tasks(task_rows)







        # 5️⃣ Mark email as read
        # service.users().messages().modify(
        #     userId="me",
        #     id=m["id"],
        #     body={"removeLabelIds": ["UNREAD"]}
        # ).execute()

        # 6️⃣ Add to response
        detailed_cat = detect_category(email_text)
        output.append({
            "id": m["id"],
            "subject": subject,
            "sender": sender,
            "body": body[:500],
            "category": label.lower(),
            "confidence": confidence,
            "detailed_category": detailed_cat,
            "has_attachment": has_attachment,
            "attachments": attachments,
            "attachment_count": len(attachments)
        })

    # return {"emails": output}
    # Fetch all stored corporate emails
    stored = supabase.table("emails") \
        .select("*") \
        .eq("is_corporate", True) \
        .limit(20)\
        .order("created_at", desc=True) \
        .execute()

    return {"emails": stored.data}
