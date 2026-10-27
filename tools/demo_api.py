"""Explicit offline demo: one saved answer plus simulated refusal/error states."""

import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from evidence_assistant.schemas import AnswerResult, Paragraph

DATA = json.loads((Path(__file__).resolve().parents[1] / "examples/demo.json").read_text("utf-8"))
REFUSAL_QUESTION = "What is the weather tomorrow?"
ERROR_QUESTION = "Show a service failure."
app = FastAPI(title="PaperTrail offline demo")


class Question(BaseModel):
    paper_id: str
    question: str


@app.middleware("http")
async def request_id(request: Request, call_next):
    request.state.request_id = uuid4().hex
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.get("/health")
def health():
    return {"status": "alive", "mode": "offline_demo"}


@app.get("/ready")
def ready():
    return {"status": "ready", "mode": "offline_demo"}


@app.get("/papers")
def papers():
    return [DATA["paper"]]


@app.get("/papers/{paper_id}/paragraphs/{paragraph_id}", response_model=Paragraph)
def paragraph(paper_id: str, paragraph_id: str):
    for source in DATA["paragraphs"]:
        if source["paper_id"] == paper_id and source["paragraph_id"] == paragraph_id:
            return source
    raise HTTPException(404, detail={"code": "paragraph_not_found"})


@app.post("/questions", response_model=AnswerResult)
def question(payload: Question, request: Request):
    if payload.paper_id != DATA["paper"]["paper_id"]:
        raise HTTPException(404, detail={"code": "paper_not_found"})
    if payload.question == ERROR_QUESTION:
        raise HTTPException(
            503,
            detail={
                "code": "rate_limited",
                "request_id": request.state.request_id,
            },
        )
    result = AnswerResult.model_validate(DATA["answer"])
    result = result.model_copy(update={"request_id": request.state.request_id})
    if payload.question == REFUSAL_QUESTION:
        return result.model_copy(
            update={
                "status": "insufficient_evidence",
                "claims": [],
                "citations": [],
                "latency_ms": 0,
                "model_id": "simulated refusal state",
            }
        )
    if payload.question != DATA["question"]:
        raise HTTPException(422, detail={"code": "invalid_request"})
    return result
