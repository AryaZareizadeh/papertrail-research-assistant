"""Local HTTP boundary for the evaluated answer pipeline; no alternate answer logic."""

import logging
import os
import re
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import Field, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from evidence_assistant.config import AppConfig, load_config
from evidence_assistant.generation import InvalidModelOutput, ProviderError
from evidence_assistant.schemas import AnswerResult, Paragraph, Record
from evidence_assistant.service import answer_question, build_answer_service
from evidence_assistant.store import get_paragraph, list_papers, list_paragraphs

logger = logging.getLogger(__name__)

MESSAGES = {
    "not_started": "The service has not finished initialization.",
    "configuration_unavailable": "The service configuration is unavailable.",
    "corpus_unavailable": "The paper corpus is unavailable.",
    "index_unavailable": "The retrieval index is unavailable.",
    "embedding_unavailable": "The retrieval model is unavailable.",
    "tokenizer_unavailable": "The generation tokenizer is unavailable.",
    "calibration_unavailable": "The generation token calibration is unavailable.",
    "generation_not_configured": "A generation model is not configured.",
    "missing_api_key": "Generation credentials are not configured.",
    "incompatible_artifacts": "The configured model or index artifacts are incompatible.",
    "service_unavailable": "The generation service is unavailable.",
    "paper_not_found": "Paper not found.",
    "paragraph_not_found": "Paragraph not found for this paper.",
    "invalid_request": "Invalid request fields.",
    "transport_error": "The generation service is unavailable. Try again later.",
    "rate_limited": "The generation service is rate limited. Try again later.",
    "provider_http_error": "The generation service request failed.",
    "invalid_answer_json": "The model returned an invalid structured answer.",
    "incomplete_output": "The model did not complete its answer.",
    "invalid_provider_response": "The generation service returned an invalid response.",
    "citation_not_supplied": "The model cited evidence outside the supplied context.",
    "invalid_claim": "The model returned an invalid claim.",
    "stale_chunk": "Source evidence changed. Reload the index.",
    "source_changed": "Source evidence changed. Reload the index.",
    "source_span_changed": "Source evidence changed. Reload the index.",
    "context_overflow": "The question exceeds the configured context budget.",
    "output_budget_exceeded": "The model exceeded its output budget.",
    "storage_unavailable": "The source or request storage is unavailable.",
    "internal_error": "The request could not be completed.",
    "not_found": "Resource not found.",
}


class QuestionRequest(Record):
    paper_id: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("paper_id", "question")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Must contain non-whitespace characters")
        return value.strip()


class SectionSummary(Record):
    section_index: int
    section_name: str
    paragraph_count: int


class PaperSummary(Record):
    paper_id: str
    title: str
    sections: list[SectionSummary]


class FieldError(Record):
    loc: list[str | int]
    msg: str
    type: str


class ErrorDetail(Record):
    code: str
    message: str
    request_id: str
    errors: list[FieldError] | None = None


class ErrorResponse(Record):
    detail: ErrorDetail


def _error_responses(*statuses):
    return {status: {"model": ErrorResponse} for status in statuses}


def _detail(request, code):
    code = code if code in MESSAGES else "service_unavailable"
    return {"code": code, "message": MESSAGES[code], "request_id": request.state.request_id}


def _adopt_request_id(request, value):
    if isinstance(value, str) and re.fullmatch(r"[a-f0-9]{32}", value):
        request.state.request_id = value


def _failure(request, status, code, *, request_id=None, headers=None):
    _adopt_request_id(request, request_id)
    return HTTPException(status_code=status, detail=_detail(request, code), headers=headers)


def _catalog(config):
    papers = list_papers(config.database_path)
    sections = {p.paper_id: {} for p in papers}
    for paragraph in list_paragraphs(config.database_path):
        by_section = sections[paragraph.paper_id]
        key = (paragraph.section_index, paragraph.section_name)
        by_section[key] = by_section.get(key, 0) + 1
    return [
        PaperSummary(
            paper_id=p.paper_id,
            title=p.title,
            sections=[
                SectionSummary(section_index=key[0], section_name=key[1], paragraph_count=count)
                for key, count in sorted(sections[p.paper_id].items())
            ],
        )
        for p in papers
    ]


def _required_artifacts(config):
    if not config.generation_model:
        return "generation_not_configured"
    required = [
        ("generation_tokenizer.json", "tokenizer_unavailable"),
        ("generation_token_calibration.json", "calibration_unavailable"),
    ]
    if config.retrieval_method != "bm25":
        required = [
            ("index_manifest.json", "index_unavailable"),
            ("embedding_model.json", "embedding_unavailable"),
            *required,
        ]
    for name, code in required:
        if not (config.artifact_dir / name).is_file():
            return code
    return None


def create_app(
    config: AppConfig | None = None, *, config_path: Path | None = None, service_factory=None
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application):
        settings = config
        if settings is None:
            try:
                settings = load_config(
                    config_path or Path(os.environ.get("PAPERTRAIL_CONFIG", "config.yaml"))
                )
            except (OSError, ValueError, TypeError):
                application.state.readiness_code = "configuration_unavailable"
        application.state.config = settings
        if settings is not None:
            try:
                application.state.catalog = _catalog(settings)
            except (OSError, ValueError, sqlite3.Error):
                application.state.readiness_code = "corpus_unavailable"
            else:
                blocked = _required_artifacts(settings) if service_factory is None else None
                if blocked:
                    application.state.readiness_code = blocked
                else:
                    try:
                        application.state.service = (service_factory or build_answer_service)(
                            settings
                        )
                        application.state.readiness_code = None
                    except ProviderError as exc:
                        application.state.readiness_code = (
                            exc.code if exc.code in MESSAGES else "service_unavailable"
                        )
                    except (OSError, ValueError, ImportError):
                        application.state.readiness_code = "incompatible_artifacts"
                    except Exception as exc:
                        logger.error(
                            "pipeline_initialization_failed error_type=%s", type(exc).__name__
                        )
                        application.state.readiness_code = "service_unavailable"
        try:
            yield
        finally:
            service = application.state.service
            client = getattr(getattr(service, "adapter", None), "client", None)
            if client is not None:
                client.close()
            application.state.service = None
            application.state.readiness_code = "not_started"

    application = FastAPI(title="PaperTrail", version="0.1.0", lifespan=lifespan)
    application.state.config = config
    application.state.service = None
    application.state.catalog = None
    application.state.readiness_code = "not_started"

    @application.middleware("http")
    async def correlate(request: Request, call_next):
        request.state.request_id = uuid4().hex
        try:
            response = await call_next(request)
        except Exception as exc:
            _adopt_request_id(request, getattr(exc, "request_id", None))
            logger.error(
                "request_failed request_id=%s error_type=%s",
                request.state.request_id,
                type(exc).__name__,
            )
            response = JSONResponse(
                status_code=500, content={"detail": _detail(request, "internal_error")}
            )
        response.headers["X-Request-ID"] = request.state.request_id
        route = getattr(request.scope.get("route"), "path", "unmatched")
        logger.info(
            "request_finished request_id=%s method=%s route=%s status=%s",
            request.state.request_id,
            request.method,
            route,
            response.status_code,
        )
        return response

    @application.exception_handler(RequestValidationError)
    async def invalid_fields(request: Request, exc):
        detail = _detail(request, "invalid_request")
        detail["errors"] = [{k: e[k] for k in ("loc", "msg", "type")} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": detail})

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc):
        detail = (
            exc.detail
            if isinstance(exc.detail, dict)
            else _detail(request, "not_found" if exc.status_code == 404 else "internal_error")
        )
        return JSONResponse(
            status_code=exc.status_code, content={"detail": detail}, headers=exc.headers
        )

    def require_catalog(request):
        if application.state.catalog is None:
            raise _failure(request, 503, application.state.readiness_code or "corpus_unavailable")
        return application.state.catalog

    def require_service(request):
        if application.state.service is None:
            raise _failure(request, 503, application.state.readiness_code or "service_unavailable")
        return application.state.service

    @application.get("/health")
    def health(request: Request):
        return {"status": "alive", "request_id": request.state.request_id}

    @application.get("/ready", responses=_error_responses(503))
    def ready(request: Request):
        service = require_service(request)
        return {
            "status": "ready",
            "request_id": request.state.request_id,
            "model_id": service.config.generation_model,
            "index_version": service.index.index_version,
        }

    @application.get("/papers", response_model=list[PaperSummary], responses=_error_responses(503))
    def papers(request: Request):
        return require_catalog(request)

    @application.get(
        "/papers/{paper_id}/paragraphs/{paragraph_id}",
        response_model=Paragraph,
        responses=_error_responses(404, 503),
    )
    def paragraph(paper_id: str, paragraph_id: str, request: Request):
        catalog = require_catalog(request)
        if paper_id not in {p.paper_id for p in catalog}:
            raise _failure(request, 404, "paper_not_found")
        try:
            source = get_paragraph(application.state.config.database_path, paper_id, paragraph_id)
        except (OSError, sqlite3.Error):
            raise _failure(request, 503, "storage_unavailable") from None
        if source is None:
            raise _failure(request, 404, "paragraph_not_found")
        return source

    @application.post(
        "/questions",
        response_model=AnswerResult,
        responses=_error_responses(404, 422, 500, 502, 503),
    )
    def questions(payload: QuestionRequest, request: Request):
        catalog = require_catalog(request)
        if payload.paper_id not in {p.paper_id for p in catalog}:
            raise _failure(request, 404, "paper_not_found")
        service = require_service(request)
        try:
            result = answer_question(
                payload.question, payload.paper_id, service.config.retrieval_method, service
            )
        except KeyError as exc:
            raise _failure(
                request, 404, "paper_not_found", request_id=getattr(exc, "request_id", None)
            ) from None
        except ProviderError as exc:
            status = (
                502
                if isinstance(exc, InvalidModelOutput) or exc.code == "provider_http_error"
                else 503
            )
            if exc.code in {"source_changed", "source_span_changed", "stale_chunk"}:
                status = 503
            if exc.code == "context_overflow":
                status = 422
            headers = (
                {"Retry-After": exc.retry_after}
                if exc.retry_after and exc.retry_after.isdigit()
                else None
            )
            raise _failure(
                request,
                status,
                exc.code,
                request_id=getattr(exc, "request_id", None),
                headers=headers,
            ) from None
        except (OSError, sqlite3.Error) as exc:
            raise _failure(
                request, 503, "storage_unavailable", request_id=getattr(exc, "request_id", None)
            ) from None
        except ValueError as exc:
            raise _failure(
                request, 503, "incompatible_artifacts", request_id=getattr(exc, "request_id", None)
            ) from None
        _adopt_request_id(request, result.request_id)
        return result

    return application


app = create_app()
