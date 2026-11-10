from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import generate_reply
from .diagnostics import analyze_seller

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
SELLER_PATH = ROOT / "data" / "seller.json"

app = FastAPI(title="Snapdeal Virtual KAM", version="1.0.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


def load_seller() -> dict[str, Any]:
    return json.loads(SELLER_PATH.read_text(encoding="utf-8"))


class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class CommitRequest(BaseModel):
    commitment: str = Field(min_length=3, max_length=500)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/seller")
def seller_snapshot() -> dict[str, Any]:
    seller = load_seller()
    return {"seller": {"seller_id": seller["seller_id"], "seller_name": seller["seller_name"], "category": seller["category"]}}


@app.get("/api/analysis")
def get_analysis() -> dict[str, Any]:
    return analyze_seller(load_seller())


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    result = analyze_seller(load_seller())
    reply, provider = generate_reply(result, request.message)
    return {"reply": reply, "provider": provider, "analysis": result}


@app.post("/api/commitment")
def commitment(request: CommitRequest) -> dict[str, str]:
    # In-memory acknowledgement for this prototype; production should persist with audit trail.
    return {
        "status": "recorded_for_demo",
        "commitment": request.commitment,
        "message": "Your commitment is captured in this demo session. A production version would persist it and schedule a consented follow-up.",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
