"""OmniAssist FastAPI application."""
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.agent import run_agent
from app.preprocessing import preprocess_query
from app.schemas import AskRequest, AskResponse

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(
    title="OmniAssist API",
    description="Autonomous customer-support & operations assistant: LangChain agent + NLTK preprocessing + ChromaDB RAG.",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "OmniAssist API is running"}

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    try:
        preprocessed = preprocess_query(request.query)
        result = await run_in_threadpool(run_agent, request.query, preprocessed["keywords"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OmniAssist failed to answer: {exc}")
    return AskResponse(
        query=request.query,
        answer=result["answer"],
        keywords=preprocessed["keywords"],
        tool_used=result["tools_used"][0] if result["tools_used"] else "none",
        tools_used=result["tools_used"],
    )
