from app.core.supabase import supabase

def insert_email(email_data: dict):
    response = supabase.table("emails").insert(email_data).execute()
    return response.data[0]

def insert_summary(summary_data: dict):
    response = supabase.table("summaries").insert(summary_data).execute()
    return response.data[0]

def insert_tasks(tasks: list):
    response = supabase.table("tasks").insert(tasks).execute()
    return response.data



def get_summaries():
    response = (
        supabase
        .table("summaries")
        .select("id, summary, email_id,confidence, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def get_tasks(completed: bool = False):
    response = (
        supabase
        .table("tasks")
        .select("id, title, due_date, priority,context,completed, email_id")
        .eq("completed", completed)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data
