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
