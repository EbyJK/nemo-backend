from fastapi import APIRouter, Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from fastapi import Body
from datetime import datetime, timedelta

router = APIRouter()

# TEMP storage (OK for now)
TOKEN_STORE = {}


CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/calendar/callback"

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

@router.get("/auth")
def google_auth():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES
    )

    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    # return {"auth_url": auth_url}
    return RedirectResponse(auth_url)


@router.get("/callback")
def google_callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Missing auth code")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES
    )

    flow.redirect_uri = REDIRECT_URI

    # Exchange code for tokens
    flow.fetch_token(code=code)

    credentials: Credentials = flow.credentials

    # Store tokens (TEMP – later we move to DB)
    TOKEN_STORE["access_token"] = credentials.token
    TOKEN_STORE["refresh_token"] = credentials.refresh_token
    TOKEN_STORE["expiry"] = credentials.expiry.isoformat()

    return {
        "message": "Google Calendar authorization successful",
        "access_token_present": credentials.token is not None,
        "refresh_token_present": credentials.refresh_token is not None
    }
    
    
@router.post("/push")
def push_task_to_calendar(
    title: str = Body(...),
    due_date: str = Body(...)
):
    if "access_token" not in TOKEN_STORE:
        return {"error": "User not authenticated with Google"}

    credentials = Credentials(
        token=TOKEN_STORE["access_token"],
        refresh_token=TOKEN_STORE["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    service = build("calendar", "v3", credentials=credentials)

    start_time = datetime.fromisoformat(due_date)
    end_time = start_time + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {
        "message": "Event created successfully",
        "event_id": created_event.get("id"),
        "event_link": created_event.get("htmlLink")
    }