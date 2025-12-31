from fastapi import FastAPI
from app.routes import classify, summarize, tasks,process

app = FastAPI(title="Nemo Backend")


app.include_router(
    classify.router,
    prefix="/classify",
    tags=["Classification"]
)

app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

app.include_router(process.router, prefix="/process-email", tags=["Orchestrator"])


@app.get("/")
def health_check():
    return {"status": "Nemo backend running"}