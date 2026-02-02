# import re

# def detect_category(subject: str, body: str):
#     text = f"{subject} {body}".lower()

#     # --- Security / OTP ---
#     if any(word in text for word in ["2-step", "otp", "verification", "security alert", "password reset"]):
#         return "security"

#     # --- Meeting / Calendar / Scheduling ---
#     if any(word in text for word in ["meeting", "schedule", "call", "google calendar", "zoom", "teams"]):
#         return "meeting"

#     # --- Tasks / Reminders ---
#     if any(word in text for word in ["reminder", "due", "deadline", "follow up", "todo"]):
#         return "task"

#     # --- Job-related ---
#     if any(word in text for word in ["job", "hiring", "recruit", "career", "interview"]):
#         return "job"

#     # --- Newsletters ---
#     if any(word in text for word in ["unsubscribe", "newsletter", "digest", "update", "summary"]):
#         return "newsletter"

#     # --- Promotions ---
#     if any(word in text for word in ["offer", "sale", "discount", "promo", "deal"]):
#         return "promotion"

#     # --- Personal detection (very simple heuristic) ---
#     if any(word in text for word in ["bro", "mom", "dad", "wanna", "hey", "miss you"]):
#         return "personal"

#     return "other"


import re

CATEGORIES = {
    "meeting": [
        r"\bmeeting\b", r"\bcall\b", r"\bconference\b",
        r"\bsync\b", r"\bcatch up\b", r"\bschedule\b",
        r"\bappointment\b"
    ],
    "task": [
        r"\bplease\b.*\b(send|review|update|complete)\b",
        r"\baction required\b", r"\bkindly\b",
        r"\bassigned\b", r"\bto-do\b"
    ],
    "deadline": [
        r"\bdeadline\b", r"\bdue\b", r"\bsubmit\b",
        r"\bEOD\b", r"\bend of day\b"
    ],
    "hr": [
        r"\bsalary\b", r"\bpayroll\b", r"\bpolicy\b",
        r"\bHR\b", r"\bleave\b", r"\bholiday\b"
    ],
    "recruitment": [
        r"\bjob\b", r"\bopening\b", r"\bhiring\b",
        r"\brecruitment\b", r"\bposition\b", r"\bcareer\b"
    ],
    "finance": [
        r"\binvoice\b", r"\bpayment\b", r"\bbudget\b",
        r"\bfinance\b", r"\btransaction\b"
    ],
    "notification": [
        r"\balert\b", r"\bverification\b",
        r"\bsecurity\b", r"\bcongratulations\b",
        r"\bupdate\b"
    ],
    "marketing": [
        r"\boffer\b", r"\bdiscount\b", r"\bpromotion\b",
        r"\bmarketing\b", r"\bsale\b"
    ],
}

def detect_category(text: str) -> str:
    text = text.lower()

    for category, patterns in CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return category

    return "none"
