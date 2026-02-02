from fastapi import APIRouter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.routes.calendar import TOKEN_STORE, CLIENT_ID, CLIENT_SECRET
from app.ml.classifier import classify_proba
from app.ml.category_classifier import detect_category
import base64

router = APIRouter()

def decode_email_body(msg):
    if msg.get("parts"):
        for part in msg["parts"]:
            try:
                data = part["body"]["data"]
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            except:
                continue
    try:
        data = msg["body"]["data"]
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except:
        return ""

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

    # FETCH UNREAD EMAILS ONLY
    result = service.users().messages().list(
        userId="me",
        maxResults=20,
        q="is:unread"
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
        email_text = subject + " " + body

        # Step 1: corporate classifier
        label, confidence = classify_proba(email_text)

        # We only keep corporate emails
        if label.lower() != "corporate":
            continue

        # Step 2: detailed category classifier
        detailed_cat = detect_category(email_text)

        output.append({
            "id": m["id"],
            "subject": subject,
            "sender": sender,
            "body": body[:500],
            "category": label.lower(),
            "confidence": confidence,
            "detailed_category": detailed_cat
        })

    return {"emails": output}
