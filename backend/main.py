"""Sloth Agent backend - FastAPI.

Open-source AI at its core: Gemma (local), TabPFN (local tabular), optional
Ollama runtime. Integrates Sentry tracing, Temporal workflows, and hooks for
every Hacktoberfest partner SDK (see integrations/).

Run:
    pip install -r requirements.txt
    uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.sloth_agent import (
    ChatMessage,
    OvernightRun,
    SlothAgent,
    sloth_agent,
    SummaryResult,
    TidyResult,
)
from models.gemma import GemmaModel, chat as gemma_chat, gemma
from models.tabpfn import TabPFNPrediction, tabpfn
from sentry_config import init_sentry, capture_agent_event

init_sentry(environment=os.environ.get("ENVIRONMENT", "development"))

app = FastAPI(title="Sloth Agent", version="0.1.0", description="Open-source AI agent that works while you laze.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------- Request / Response models -----------------------------

class SummarizeRequest(BaseModel):
    messages: List[dict]
    source: str = "inbox"


class SummarizeResponse(BaseModel):
    summary: str
    source: str
    generated_at: str
    model: str


class TidyRequest(BaseModel):
    directory: str
    dry_run: bool = True


class TidyResponse(BaseModel):
    actions: List[str]
    before_count: int
    after_count: int


class PredictRequest(BaseModel):
    csv_path: str
    target_column: str


class PredictResponse(BaseModel):
    target_column: str
    prediction: str
    confidence: Optional[float]
    model: str
    local: bool
    cost_usd: float


class ChatRequest(BaseModel):
    prompt: str
    system: Optional[str] = None


class ChatResponse(BaseModel):
    text: str
    model: str
    local: bool
    cost_usd: float


class OvernightRequest(BaseModel):
    run_id: str
    messages: List[dict]
    directory: str = "."
    csv_path: Optional[str] = None
    target_column: Optional[str] = None


class OvernightResponse(BaseModel):
    run_id: str
    status: str
    summary: Optional[str]
    tidy_actions: List[str]
    predictions: List[dict]
    started_at: str
    finished_at: Optional[str]


# ----------------------------- Routes -----------------------------


@app.get("/")
def root():
    return {
        "name": "Sloth Agent",
        "theme": "Slow and Steady - open-source AI that works while you laze",
        "runtime": "local open-weight (Gemma) + TabPFN",
        "ai_is_local": True,
        "cost_per_run_usd": 0.0,
        "prize_categories": [
            "Gemma", "TabPFN", "Mastra", "Sentry", "Temporal", "MongoDB Atlas",
            "SerpApi", "Browserbase", "ElevenLabs", "Auth0", "Backboard", "Entire",
            "GitHub Copilot", "Render", "DigitalOcean", ".tech Domains", "Tinker",
            "Arduino", "Ultramarine", "Tiger Data",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemma_backend": gemma.backend if hasattr(gemma, "backend") else "unknown",
        "tabpfn_backend": tabpfn.backend,
        "local_only": True,
    }


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    """Read overnight messages -> two-line summary (laziness reward #1)."""
    msgs = [ChatMessage(**m) for m in req.messages]
    result: SummaryResult = sloth_agent.summarize_messages(msgs, source=req.source)
    capture_agent_event("summarize", {"source": req.source, "model": result.model})
    return SummarizeResponse(
        summary=result.summary,
        source=result.source,
        generated_at=result.generated_at,
        model=result.model,
    )


@app.post("/tidy", response_model=TidyResponse)
def tidy(req: TidyRequest):
    """Sort/rename/archive clutter (laziness reward #2)."""
    result: TidyResult = sloth_agent.tidy_files(req.directory, dry_run=req.dry_run)
    capture_agent_event("tidy", {"directory": req.directory, "dry_run": str(req.dry_run)})
    return TidyResponse(
        actions=result.actions,
        before_count=result.before_count,
        after_count=result.after_count,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """Tabular forecast/classify from CSV (laziness reward #3)."""
    result = sloth_agent.predict_csv(req.csv_path, req.target_column)
    capture_agent_event("predict", {"target": req.target_column, "model": result["model"]})
    return PredictResponse(**result)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Chat with Gemma, your local open-weight model."""
    response = gemma_chat(req.prompt, system=req.system)
    capture_agent_event("chat", {"model": response.model, "local": str(response.local)})
    return ChatResponse(
        text=response.text,
        model=response.model,
        local=response.local,
        cost_usd=response.cost_usd,
    )


@app.post("/overnight", response_model=OvernightResponse)
def overnight(req: OvernightRequest):
    """Full lazy suite: summarize + tidy + predict. Run while you sleep."""
    run: OvernightRun = sloth_agent.overnight_run(
        run_id=req.run_id,
        messages=[ChatMessage(**m) for m in req.messages],
        directory=req.directory,
        csv_path=req.csv_path,
        target_column=req.target_column,
    )
    capture_agent_event("overnight_run", {"run_id": req.run_id, "status": run.status})
    return OvernightResponse(
        run_id=run.id,
        status=run.status,
        summary=run.summary,
        tidy_actions=run.tidy_actions,
        predictions=run.predictions,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    run = sloth_agent.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run_id": run.id,
        "status": run.status,
        "summary": run.summary,
        "tidy_actions": run.tidy_actions,
        "predictions": run.predictions,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
    }


@app.get("/demo")
def demo():
    """One-click demo: run the full lazy suite with sample data."""
    return overnight(OvernightRequest(
        run_id="demo-run",
        messages=[
            {"sender": "Alice", "text": "Dinner Thursday?", "timestamp": "22:15"},
            {"sender": "Group", "text": "Meeting moved to 10am.", "timestamp": "23:02"},
        ],
        directory=".",
    ))
