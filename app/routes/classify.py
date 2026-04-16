






# from cProfile import label
# from fastapi import APIRouter
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# # from app.routes.calendar import TOKEN_STORE, CLIENT_ID, CLIENT_SECRET
# from app.ml.classifier import classify_proba
# from app.ml.category_classifier import detect_category    # <-- NEW
# from email import message_from_bytes
# import base64
# from app.ml.category_classifier import detect_category

# import os

# CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# router = APIRouter()


# # def decode_email_body(msg):
# #     if msg.get("parts"):
# #         for part in msg["parts"]:
# #             try:
# #                 data = part["body"]["data"]
# #                 decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
# #                 return decoded
# #             except:
# #                 continue
# #     try:
# #         data = msg["body"]["data"]
# #         decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
# #         return decoded
# #     except:
# #         return ""
# def decode_email_body(payload):
#     body = ""

#     if "parts" in payload:
#         for part in payload["parts"]:
#             # Look for text/plain part
#             if part.get("mimeType") == "text/plain":
#                 data = part["body"].get("data")
#                 if data:
#                     body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
#                     return body

#             # Sometimes nested parts
#             if "parts" in part:
#                 for subpart in part["parts"]:
#                     if subpart.get("mimeType") == "text/plain":
#                         data = subpart["body"].get("data")
#                         if data:
#                             body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
#                             return body

#     # fallback (single-part email)
#     if payload.get("body", {}).get("data"):
#         data = payload["body"]["data"]
#         body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

#     return body



# @router.get("/list")
# def list_emails():
#     if "access_token" not in TOKEN_STORE:
#         return {"error": "User not authenticated"}

#     creds = Credentials(
#         token=TOKEN_STORE["access_token"],
#         refresh_token=TOKEN_STORE["refresh_token"],
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET
#     )

#     service = build("gmail", "v1", credentials=creds)

#     result = service.users().messages().list(
#         userId="me", maxResults=20
#     ).execute()

#     messages = result.get("messages", [])
#     output = []

#     for m in messages:
#         msg = service.users().messages().get(
#             userId="me", id=m["id"], format="full"
#         ).execute()

#         headers = msg["payload"]["headers"]
#         subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
#         sender = next((h["value"] for h in headers if h["name"] == "From"), "")

#         body = decode_email_body(msg["payload"])

#         # ---- ML classifier (corporate/non-corporate) ----
#         label, confidence = classify_proba(subject + " " + body)
#         is_corporate = (label == "corporate")

#         print(" DEBUG: classify.py is running")
#         # ---------------------------------------------
#         # BUSINESS KEYWORD BOOST (Rule-based override)
#         # ---------------------------------------------
#         business_keywords = [
#             "project", "status", "update", "action", "required",
#             "deliverable", "review", "meeting", "schedule",
#             "submit", "report", "documentation", "deadline"
#         ]

#         subject_lower = subject.lower()

#         # If subject contains corporate/business words → force corporate
#         if any(word in subject_lower for word in business_keywords):
#             is_corporate = True
        
#         # NEW → detect detailed category only if corporate
#         # if label == "corporate":
#         if is_corporate:
#           detailed = detect_category(subject + " " + body)
#         else:
#             detailed = "none"
#         # ---- NEW: category detection ----
#         category = detect_category(subject, body)

#         output.append({
#             "id": m["id"],
#             "subject": subject,
#             "sender": sender,
#             "body": body[:500],
#             # "is_corporate": label.lower(),
#             "is_corporate": is_corporate,
#             "category": category,         # <---- NEW CATEGORY
#             "confidence": confidence,
#              "detailed_category": detailed,
#         })

#     return {"emails": output}







from fastapi import APIRouter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest

from app.ml.classifier import classify_proba
from app.ml.category_classifier import detect_category
from app.core.supabase import supabase

import base64
import os

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


# ---------------- DECODE EMAIL ---------------- #

def decode_email_body(payload):
    body = ""

    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

            if "parts" in part:
                for subpart in part["parts"]:
                    if subpart.get("mimeType") == "text/plain":
                        data = subpart["body"].get("data")
                        if data:
                            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    if payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return body


# ---------------- MAIN API ---------------- #

@router.get("/list")
def list_emails():

    user_id = "5255d7c4-60ad-4120-941f-94ae6ebbbc3d"

    # 🔥 FETCH TOKENS FROM SUPABASE
    response = supabase.table("google_accounts") \
        .select("*") \
        .eq("user_id", user_id) \
        .single() \
        .execute()

    if not response.data:
        return {"error": "User not authenticated"}

    account = response.data

    credentials = Credentials(
        token=account["access_token"],
        refresh_token=account["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    # 🔥 AUTO REFRESH TOKEN
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(GoogleRequest())

        supabase.table("google_accounts").update({
            "access_token": credentials.token,
            "expires_at": credentials.expiry.isoformat()
        }).eq("user_id", user_id).execute()

    service = build("gmail", "v1", credentials=credentials)

    result = service.users().messages().list(
        userId="me", maxResults=20
    ).execute()

    messages = result.get("messages", [])
    output = []

    for m in messages:
        msg = service.users().messages().get(
            userId="me", id=m["id"], format="full"
        ).execute()

        headers = msg["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        body = decode_email_body(msg["payload"])

        # ML classification
        label, confidence = classify_proba(subject + " " + body)
        is_corporate = (label == "corporate")

        # rule-based boost
        business_keywords = [
            "project", "status", "update", "action", "required",
            "deliverable", "review", "meeting", "schedule",
            "submit", "report", "documentation", "deadline"
        ]

        subject_lower = subject.lower()

        if any(word in subject_lower for word in business_keywords):
            is_corporate = True

        # detailed category
        if is_corporate:
            detailed = detect_category(subject + " " + body)
        else:
            detailed = "none"

        category = detect_category(subject, body)

        output.append({
            "id": m["id"],
            "subject": subject,
            "sender": sender,
            "body": body[:500],
            "is_corporate": is_corporate,
            "category": category,
            "confidence": confidence,
            "detailed_category": detailed,
        })

    return {"emails": output}




