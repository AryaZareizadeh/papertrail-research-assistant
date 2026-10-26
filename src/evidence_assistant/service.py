"""One question-to-citation pipeline shared by CLI, future evaluation, and API."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, text_hash
from evidence_assistant.generation import (
    ANSWER_SCHEMA,
    GENERATION_OPTIONS,
    SYSTEM_PROMPT,
    GroqAdapter,
    InvalidModelOutput,
    ProviderError,
    build_messages,
    evidence_records,
    parse_draft,
    validate_draft,
)
from evidence_assistant.retrieval import RetrievalIndex, retrieve
from evidence_assistant.schemas import AnswerResult, Citation, DraftAnswer, RetrievedChunk
from evidence_assistant.store import get_chunk, get_paper, get_paragraph, write_run


@dataclass
class AnswerService:
    config: AppConfig
    index: RetrievalIndex
    counter: object
    adapter: GroqAdapter
    purpose: str = "application"


def prepare_context(question, paper, retrieved, config, counter):
    """Shared whole-chunk budgeting for application and offline retrieval scoring."""
    supplied = list(retrieved)
    input_limit = (
        config.generator_context_tokens
        - config.max_output_tokens
        - config.context_safety_margin_tokens
    )
    while True:
        messages = build_messages(question, paper, supplied)
        estimated = counter.count_prompt(messages, ANSWER_SCHEMA)
        evidence_tokens = (
            counter.count_text(json.dumps(evidence_records(supplied), ensure_ascii=False))
            if supplied
            else 0
        )
        if estimated <= input_limit and evidence_tokens <= config.max_evidence_tokens:
            return supplied, messages, estimated, evidence_tokens
        if not supplied:
            raise ProviderError(
                "Question/instructions exceed the configured context budget",
                code="context_overflow",
            )
        supplied.pop()


def answer_question(
    question: str,
    paper_id: str,
    method: str,
    service: AnswerService,
    *,
    fixed_context: list[RetrievedChunk] | None = None,
) -> AnswerResult:
    config = service.config
    started, request_id = perf_counter(), uuid4().hex
    configuration = config.model_dump(mode="json")
    stage = "input_validation"
    record = {
        "request_id": request_id,
        "purpose": service.purpose,
        "status": "error",
        "created_at": datetime.now(UTC).isoformat(),
        "paper_id": paper_id,
        "question": question,
        "method": method,
        "model_id": config.generation_model,
        "prompt_version": config.prompt_version,
        "index_version": service.index.index_version,
        "token_counter": service.counter.identity,
        "prompt_sha256": text_hash(SYSTEM_PROMPT + json.dumps(ANSWER_SCHEMA, sort_keys=True)),
        "configuration": configuration,
        "configuration_sha256": text_hash(json.dumps(configuration, sort_keys=True)),
        "requested_generation_options": getattr(
            service.adapter,
            "request_settings",
            {
                **GENERATION_OPTIONS,
                "max_completion_tokens": config.max_output_tokens,
            },
        ),
        "attempts": 0,
        "attempt_log": [],
        "retrieved_chunk_ids": [],
        "supplied_chunk_ids": [],
        "token_usage": {
            "input_tokens_estimated": 0,
            "input_tokens_actual": None,
            "output_tokens_actual": None,
            "evidence_tokens": 0,
            "counter_verified": False,
        },
    }
    try:
        if not question.strip() or len(question) > 2000:
            raise ValueError("Question must contain 1–2000 characters")
        paper = get_paper(config.database_path, paper_id)
        if paper is None:
            raise KeyError(f"Unknown paper: {paper_id}")
        record["source_revision"] = paper.source_revision
        record["source_hash"] = file_hash(config.database_path)
        stage = "retrieval"
        if fixed_context is None:
            retrieved = retrieve(question, paper_id, method, config.top_k, service.index)
        else:
            retrieved = list(fixed_context)
            record["retrieval_mode"] = "fixed_comparison_context"
            if len(retrieved) > config.top_k or len({r.chunk.chunk_id for r in retrieved}) != len(
                retrieved
            ):
                raise ValueError("Fixed context must contain unique chunks within top_k")
            if any(get_chunk(config.database_path, r.chunk.chunk_id) != r.chunk for r in retrieved):
                raise ValueError("Fixed context differs from stored source chunks")
        record["retrieved_chunk_ids"] = [r.chunk.chunk_id for r in retrieved]
        if any(r.chunk.paper_id != paper_id for r in retrieved):
            raise InvalidModelOutput("Retrieved context contains a different paper")
        stage = "context_budget"
        input_limit = (
            config.generator_context_tokens
            - config.max_output_tokens
            - config.context_safety_margin_tokens
        )
        supplied, messages, estimated, evidence_tokens = prepare_context(
            question, paper, retrieved, config, service.counter
        )
        if fixed_context is not None and len(supplied) != len(retrieved):
            raise ProviderError(
                "Fixed comparison context exceeds the candidate budget",
                code="fixed_context_budget_exceeded",
            )
        effective_messages = getattr(service.adapter, "effective_messages", lambda m, s: m)(
            messages, ANSWER_SCHEMA
        )
        record["effective_messages_sha256"] = text_hash(
            json.dumps(effective_messages, sort_keys=True)
        )
        record["supplied_chunk_ids"] = [r.chunk.chunk_id for r in supplied]
        record["token_usage"].update(
            {"input_tokens_estimated": estimated, "evidence_tokens": evidence_tokens}
        )
        if supplied:
            stage = "generation"
            reply = service.adapter.generate(messages, ANSWER_SCHEMA)
            record["attempts"] = reply.attempts
            record["attempt_log"] = reply.attempt_log
            record["provider_fingerprint"] = reply.fingerprint
            record["provider_model_id"] = reply.model_id
            record["provider_cost_usd"] = reply.cost_usd
            record["token_usage"].update(
                {
                    "input_tokens_actual": reply.input_tokens,
                    "output_tokens_actual": reply.output_tokens,
                    "counter_verified": reply.input_tokens == estimated,
                }
            )
            if reply.input_tokens > input_limit:
                raise ProviderError(
                    "Provider's actual prompt exceeds the configured context budget",
                    code="context_overflow",
                )
            if reply.output_tokens > config.max_output_tokens:
                raise ProviderError(
                    "Provider exceeded the configured output budget", code="output_budget_exceeded"
                )
            stage = "draft_validation"
            draft = parse_draft(reply.content)
            validate_draft(draft, supplied)
        else:
            draft = DraftAnswer(status="insufficient_evidence", claims=[])
            record["token_usage"].update({"input_tokens_actual": 0, "output_tokens_actual": 0})
            record["generation_skipped"] = True
        stage = "citation_validation"
        by_id = {r.chunk.chunk_id: r.chunk for r in supplied}
        citations = {}
        for claim in draft.claims:
            for cid in claim.citation_chunk_ids:
                chunk = get_chunk(config.database_path, cid)
                if chunk is None or chunk != by_id[cid]:
                    raise InvalidModelOutput(
                        "Citation refers to a stale source chunk", code="stale_chunk"
                    )
                source = get_paragraph(config.database_path, paper_id, chunk.paragraph_id)
                if source is None or text_hash(source.text) != source.text_sha256:
                    raise InvalidModelOutput(
                        "Citation source is missing or changed", code="source_changed"
                    )
                quote = source.text[chunk.start_char : chunk.end_char]
                if quote != chunk.text:
                    raise InvalidModelOutput(
                        "Citation source span has changed", code="source_span_changed"
                    )
                citations[cid] = Citation(
                    chunk_id=cid,
                    paper_id=paper_id,
                    paragraph_id=chunk.paragraph_id,
                    section_name=source.section_name,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    quote=quote,
                )
        result = AnswerResult(
            request_id=request_id,
            paper_id=paper_id,
            status=draft.status,
            claims=draft.claims,
            citations=list(citations.values()),
            retrieved_chunk_ids=record["supplied_chunk_ids"],
            method=method,
            model_id=config.generation_model,
            prompt_version=config.prompt_version,
            index_version=service.index.index_version,
            latency_ms=(perf_counter() - started) * 1000,
        )
        record.update({"status": result.status, "result": result.model_dump()})
        return result
    except Exception as exc:
        exc.request_id = request_id
        record.update(
            {
                "status": "error",
                "error_type": type(exc).__name__,
                "error_stage": stage,
                "error_code": "internal_error",
            }
        )
        if isinstance(exc, ProviderError):
            record["error_code"] = exc.code
            record["token_usage"].update(exc.usage)
            record["attempts"] = max(record["attempts"], exc.attempts)
            record["retry_after"] = exc.retry_after
            if exc.attempt_log:
                record["attempt_log"] = exc.attempt_log
        raise
    finally:
        record["latency_ms"] = (perf_counter() - started) * 1000
        write_run(config.report_dir / "runs", record)


def build_answer_service(
    config: AppConfig, method: str | None = None, *, use_calibration: bool = True
) -> AnswerService:
    from evidence_assistant.generation_tokens import GenerationCounter

    if not config.generation_model:
        raise ValueError("Configure a generation model before answering")
    adapter = GroqAdapter(config)
    return AnswerService(
        config=config,
        adapter=adapter,
        counter=GenerationCounter.load(config, use_calibration=use_calibration),
        index=RetrievalIndex.load(config, method=method or config.retrieval_method),
    )
