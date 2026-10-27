"""An offline generation-backend comparison on immutable baseline passages."""

import json
import shutil
import time
from datetime import UTC, datetime

from evidence_assistant.checkpoint import atomic_json as _atomic_json
from evidence_assistant.checkpoint import restore_checkpoint as _restore_checkpoint
from evidence_assistant.checkpoint import save_checkpoint as _save_checkpoint
from evidence_assistant.data import file_hash, read_jsonl, text_hash, write_json
from evidence_assistant.evaluation import EvaluationPolicy, evaluate_answers, evaluate_retrieval
from evidence_assistant.evaluation_runs import (
    _enrich_record,
    _hash,
    report_run,
    scoring_identity,
    snapshot,
)
from evidence_assistant.generation import ANSWER_SCHEMA, SYSTEM_PROMPT, ProviderError
from evidence_assistant.requesty import build_candidate_service, candidate_config
from evidence_assistant.schemas import Chunk, GoldQuestion, Paragraph, RetrievedChunk
from evidence_assistant.service import answer_question


def run_comparison(config, source, output, *, method="hybrid", interval_seconds=15, service=None):
    started = time.perf_counter()
    source_manifest = json.loads((source / "manifest.json").read_text("utf-8"))
    if source_manifest["split"] == "test" or not source_manifest["qa"]:
        raise ValueError("Use a validation/debug answer baseline, never held-out test output")
    for name, digest in {
        **source_manifest["scoring_input_hashes"],
        "predictions.jsonl": source_manifest["prediction_sha256"],
    }.items():
        if file_hash(source / name) != digest:
            raise ValueError("Baseline scoring inputs changed")
    references = [GoldQuestion(**q) for q in read_jsonl(source / "references.jsonl")]
    baseline_rows = [r for r in read_jsonl(source / "predictions.jsonl") if r["method"] == method]
    baseline = {r["question_id"]: r for r in baseline_rows}
    if len(baseline) != len(baseline_rows) or set(baseline) != {q.question_id for q in references}:
        raise ValueError("Baseline must retain exactly one result per selected question/method")
    corpus_hash = file_hash(config.database_path)
    prompt_hash = text_hash(SYSTEM_PROMPT + json.dumps(ANSWER_SCHEMA, sort_keys=True))
    controls = (
        "top_k",
        "max_output_tokens",
        "max_evidence_tokens",
        "generator_context_tokens",
        "context_safety_margin_tokens",
        "prompt_version",
    )
    for q in references:
        row = baseline[q.question_id]
        if row["paper_id"] != q.paper_id or row["question"] != q.question:
            raise ValueError("Baseline question differs from its reference selection")
        if row["source_hash"] != corpus_hash or row["prompt_sha256"] != prompt_hash:
            raise ValueError("Baseline source/prompt differs from the current comparison")
        if any(row["configuration"][name] != getattr(config, name) for name in controls):
            raise ValueError("Comparison control settings differ from the baseline")
        if [c["chunk_id"] for c in row["supplied_passages"]] != row["supplied_chunk_ids"]:
            raise ValueError("Baseline passage order/IDs differ")
    if interval_seconds < 0:
        raise ValueError("Request interval must be nonnegative")
    candidate = candidate_config(config)
    supplied_service = service is not None
    if service is None:
        service = build_candidate_service(config)
    if service.config.generation_model != candidate.generation_model:
        raise ValueError("Comparison service model differs from the declared candidate")
    service.purpose = "fixed_context_model_comparison"
    metadata_files = {
        name: candidate.artifact_dir / "requesty" / name
        for name in ("tokenizer_metadata.json", "calibration.json")
    }
    binding = {
        "source_manifest_sha256": file_hash(source / "manifest.json"),
        "source_predictions_sha256": source_manifest["prediction_sha256"],
        "base_snapshot": snapshot(config),
        "candidate_config": candidate.model_dump(mode="json"),
        "candidate_token_counter": service.counter.identity,
        "candidate_artifacts": {
            name: file_hash(path) if path.exists() else None
            for name, path in metadata_files.items()
        },
        "method": method,
        "synthetic_service_injected": supplied_service,
    }
    path = output / "manifest.json"
    output.mkdir(parents=True, exist_ok=True)
    if path.exists():
        saved = json.loads(path.read_text("utf-8"))
        if saved["binding"] != binding or saved["sha256"] != _hash(binding):
            raise ValueError("Comparison resume settings differ")
    else:
        saved = {
            "run_id": output.name,
            "split": source_manifest["split"],
            "qa": True,
            "methods": [method],
            "created_at": datetime.now(UTC).isoformat(),
            "binding": binding,
            "sha256": _hash(binding),
            "scoring_identity": scoring_identity(),
            "scoring_input_hashes": source_manifest["scoring_input_hashes"],
            "comparison_source": str(source.resolve()),
            "format_limitation": "Groq strict schema; Requesty prompt-embedded identical schema",
            "cold_startup_ms": (time.perf_counter() - started) * 1000,
        }
        for name in ("references.jsonl", "paragraphs.jsonl"):
            shutil.copyfile(source / name, output / name)
        _atomic_json(path, saved, json_writer=write_json)
    saved, rows = _restore_checkpoint(output, saved, json_writer=write_json)
    done = {r["question_id"] for r in rows}
    if len(done) != len(rows) or not done <= set(baseline):
        raise ValueError("Comparison contains duplicate or unselected cases")
    previous = None
    for q in references:
        if q.question_id in done:
            continue
        if previous is not None:
            time.sleep(max(0, interval_seconds - (time.monotonic() - previous)))
        previous = time.monotonic()
        original = baseline[q.question_id]
        context = [
            RetrievedChunk(chunk=Chunk(**c), rank=i + 1, score=0, method=method)
            for i, c in enumerate(original["supplied_passages"])
        ]
        try:
            answer = answer_question(q.question, q.paper_id, method, service, fixed_context=context)
            request_id = answer.request_id
        except ProviderError as exc:
            request_id = exc.request_id
        record = json.loads(
            (candidate.report_dir / "runs" / f"{request_id}.json").read_text("utf-8")
        )
        row = _enrich_record(q, record, candidate)
        row["baseline_request_id"] = original["request_id"]
        row["context_identical"] = row["supplied_passages"] == original["supplied_passages"]
        row["baseline_index_version"] = original["index_version"]
        if row["status"] != "error" and not row["context_identical"]:
            raise ValueError("Candidate context differs; comparison cannot continue")
        rows.append(row)
        saved = _save_checkpoint(output, saved, rows, json_writer=write_json)
        print(f"{output.name}: {len(rows)}/{len(references)} {row['status']}", flush=True)
        if row.get("error_code") in {"rate_limited", "unexpected_provider_cost"}:
            break
    metrics = report_run(output)
    paragraphs = [Paragraph(**p) for p in read_jsonl(source / "paragraphs.jsonl")]
    result = {
        "paired_cases": len(rows),
        "selected_questions": len(references),
        "identical_context_cases": sum(r["context_identical"] for r in rows),
        "baseline": {
            "answers": evaluate_answers(baseline, references, paragraphs, EvaluationPolicy()),
            "retrieval": evaluate_retrieval(baseline, references, paragraphs, EvaluationPolicy()),
        },
        "candidate": metrics["methods"][method],
        "manifest_sha256": file_hash(path),
    }
    write_json(output / "paired_metrics.json", result)
    return result
