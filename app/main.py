"""OmniAssist FastAPI application.

The pipeline for every request:
    user query -> NLTK preprocessing -> LangChain agent (tool calling) -> structured JSON
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.agent import run_agent
from app.preprocessing import preprocess_query
from app.schemas import AskRequest, AskResponse

# Load the project's own .env (OPENAI_API_KEY etc.) no matter where uvicorn is started from.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(
    title="OmniAssist API",
    description=(
        "Autonomous customer-support & operations assistant: "
        "LangChain agent + NLTK preprocessing + ChromaDB RAG."
    ),
    version="1.0.0",
)


@app.get("/")
async def root():
    """Simple health-check / welcome message."""
    return {"message": "OmniAssist API is running"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """Answer a customer-support query and report which tool was used."""
    try:
        # 1. NLTK preprocessing: clean the query and extract keywords.
        preprocessed = preprocess_query(request.query)

        # 2. LangChain agent picks and calls the right tool(s), then writes the
        #    answer. The agent call is blocking, so it runs in a worker thread
        #    to keep the event loop free.
        result = await run_in_threadpool(run_agent, request.query, preprocessed["keywords"])
    except Exception as exc:  # keep the API alive even when a single query fails
        raise HTTPException(status_code=500, detail=f"OmniAssist failed to answer: {exc}")

    # 3. Structured JSON response (Pydantic validates it before it is sent).
    return AskResponse(
        query=request.query,
        answer=result["answer"],
        keywords=preprocessed["keywords"],
        tool_used=result["tools_used"][0] if result["tools_used"] else "none",
        tools_used=result["tools_used"],
    )
