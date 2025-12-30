from fastapi import FastAPI
from app.routes import classify, summarize, tasks

app = FastAPI(title="Nemo Backend")

app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@app.get("/")
def health():
    return {"status": "Nemo backend running"}
