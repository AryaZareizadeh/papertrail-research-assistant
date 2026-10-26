"""Reproducible offline experiments, checkpointing, and held-out test gates."""

import json
import platform
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, read_jsonl, text_hash, write_json, write_jsonl
from evidence_assistant.evaluation import (
    EvaluationPolicy,
    eligibility_summary,
    evaluate_answers,
    evaluate_retrieval,
    official_prediction,
    official_source_identity,
)
from evidence_assistant.generation import (
    ANSWER_SCHEMA,
    GENERATION_OPTIONS,
    SYSTEM_PROMPT,
    ProviderError,
)
from evidence_assistant.schemas import GoldQuestion
from evidence_assistant.service import AnswerService, answer_question, prepare_context
from evidence_assistant.store import get_chunk, get_paper, list_papers, list_paragraphs


def _hash(value):
    return text_hash(json.dumps(value, sort_keys=True))


def snapshot(config: AppConfig):
    """Hash every input that changes predictions, selection, or scoring; never keys."""
    root = Path(__file__).parent
    required = {
        "corpus": config.database_path,
        "index": config.artifact_dir / "index_manifest.json",
        "chunking": config.artifact_dir / "chunking_manifest.json",
        "generation_tokenizer": config.artifact_dir / "generation_tokenizer.json",
        "generation_calibration": config.artifact_dir / "generation_token_calibration.json",
        "questions": config.evaluation_dir / "questions.jsonl",
        "dataset": config.manifest_dir / "data_manifest.json",
        "validation_selection": config.manifest_dir / "validation_pilot.json",
        "test_selection": config.manifest_dir / "test_pilot.json",
        "dependency_lock": root.parents[1] / "requirements.lock.txt",
    }
    return {
        "config": config.model_dump(mode="json"),
        "input_hashes": {name: file_hash(path) for name, path in required.items()},
        "code_hashes": {p.name: file_hash(p) for p in sorted(root.glob("*.py"))},
        "policy": EvaluationPolicy().snapshot(),
        "official": official_source_identity(),
        "prompt": _hash(
            {"system": SYSTEM_PROMPT, "schema": ANSWER_SCHEMA, "options": GENERATION_OPTIONS}
        ),
    }


def freeze_run(config, output):
    if output.exists():
        raise ValueError("Frozen manifest already exists; choose a new path")
    payload = snapshot(config)
    result = {
        "created_at": datetime.now(UTC).isoformat(),
        "snapshot": payload,
        "sha256": _hash(payload),
    }
    write_json(output, result)
    return result


def validate_frozen_run(config, path):
    record = json.loads(path.read_text("utf-8"))
    if _hash(record["snapshot"]) != record["sha256"] or snapshot(config) != record["snapshot"]:
        raise ValueError("Current settings/data/code differ from the frozen run manifest")
    return record["sha256"]


def load_cases(config, split, manifest, limit=None):
    selection = json.loads(manifest.read_text("utf-8"))
    if selection["split"] != split:
        raise ValueError("Selection manifest split differs from requested split")
    indexed = {p.paper_id: p for p in list_papers(config.database_path)}
    ids = selection["paper_ids"]
    if len(set(ids)) != len(ids) or not ids:
        raise ValueError("Selection must contain unique indexed paper IDs")
    if any(pid not in indexed or indexed[pid].split != split for pid in ids):
        raise ValueError("Selection papers must be indexed in the requested split")
    questions = [
        GoldQuestion(**r)
        for r in read_jsonl(config.evaluation_dir / "questions.jsonl")
        if r["paper_id"] in ids
    ]
    if "question_ids" in selection:
        wanted = selection["question_ids"]
        if len(set(wanted)) != len(wanted) or not set(wanted) <= {q.question_id for q in questions}:
            raise ValueError("Question selection includes duplicates or IDs outside its papers")
        questions = [q for q in questions if q.question_id in wanted]
    questions.sort(key=lambda q: text_hash(f"{config.seed}:{q.question_id}"))
    if limit is not None:
        if limit < 1 or split == "test":
            raise ValueError("A positive limit is allowed only before final test evaluation")
        questions = questions[:limit]
    if not questions:
        raise ValueError("Selection has no questions")
    return questions


def _context_record(question, method, service):
    from evidence_assistant.retrieval import retrieve

    started = time.perf_counter()
    paper = get_paper(service.config.database_path, question.paper_id)
    ranked = retrieve(
        question.question, question.paper_id, method, service.config.top_k, service.index
    )
    supplied, _, estimated, evidence = prepare_context(
        question.question, paper, ranked, service.config, service.counter
    )
    return {
        "status": "retrieval_only",
        "question_id": question.question_id,
        "paper_id": question.paper_id,
        "question": question.question,
        "method": method,
        "retrieved_chunk_ids": [r.chunk.chunk_id for r in ranked],
        "supplied_chunk_ids": [r.chunk.chunk_id for r in supplied],
        "supplied_paragraph_ids": list(dict.fromkeys(r.chunk.paragraph_id for r in supplied)),
        "supplied_passages": [r.chunk.model_dump() for r in supplied],
        "token_usage": {"input_tokens_estimated": estimated, "evidence_tokens": evidence},
        "latency_ms": (time.perf_counter() - started) * 1000,
    }


def _enrich_record(question, record, config):
    chunks = [get_chunk(config.database_path, cid) for cid in record["supplied_chunk_ids"]]
    if any(c is None for c in chunks):
        raise ValueError("Saved prediction refers to missing source chunks")
    return {
        **record,
        "question_id": question.question_id,
        "supplied_passages": [c.model_dump() for c in chunks],
        "supplied_paragraph_ids": list(dict.fromkeys(c.paragraph_id for c in chunks)),
    }


def scoring_identity():
    from evidence_assistant import evaluation

    return {
        "policy": EvaluationPolicy().snapshot(),
        "official": official_source_identity(),
        "scoring_code_sha256": file_hash(Path(evaluation.__file__)),
        "report_code_sha256": file_hash(Path(__file__)),
    }


def report_run(run_dir):
    manifest = json.loads((run_dir / "manifest.json").read_text("utf-8"))
    if manifest.get("scoring_identity") != scoring_identity():
        raise ValueError("Saved scoring identity differs; use the original code to report this run")
    if any(
        file_hash(run_dir / name) != value
        for name, value in manifest["scoring_input_hashes"].items()
    ):
        raise ValueError("Saved scoring inputs changed")
    prediction_path = run_dir / "predictions.jsonl"
    if manifest.get("prediction_sha256") is not None and (
        not prediction_path.exists() or file_hash(prediction_path) != manifest["prediction_sha256"]
    ):
        raise ValueError("Saved scoring predictions changed")
    questions = [GoldQuestion(**r) for r in read_jsonl(run_dir / "references.jsonl")]
    from evidence_assistant.schemas import Paragraph

    paragraphs = [Paragraph(**r) for r in read_jsonl(run_dir / "paragraphs.jsonl")]
    rows = (
        read_jsonl(run_dir / "predictions.jsonl")
        if (run_dir / "predictions.jsonl").exists()
        else []
    )
    policy, methods = EvaluationPolicy(), {}
    for method in manifest["methods"]:
        selected = [r for r in rows if r["method"] == method]
        if len({r["question_id"] for r in selected}) != len(selected):
            raise ValueError("Duplicate evaluation predictions")
        predictions = {r["question_id"]: r for r in selected}
        methods[method] = {
            "retrieval": evaluate_retrieval(predictions, questions, paragraphs, policy)
        }
        if manifest["qa"]:
            methods[method]["answers"] = evaluate_answers(
                predictions, questions, paragraphs, policy
            )
            adapted = [
                official_prediction(q.question_id, predictions.get(q.question_id, {}), paragraphs)
                for q in questions
            ]
            write_jsonl(
                run_dir / f"{method}_official_predictions.jsonl",
                [p for p in adapted if p is not None],
            )
        usage = [r.get("token_usage", {}) for r in selected]
        methods[method]["usage"] = {
            key: {
                "sum_known": sum(u[key] for u in usage if u.get(key) is not None),
                "unknown_records": sum(u.get(key) is None for u in usage),
            }
            for key in ("input_tokens_actual", "output_tokens_actual")
        }
        methods[method]["error_codes"] = dict(
            Counter(r.get("error_code") for r in selected if r["status"] == "error")
        )
    result = {
        "run_id": manifest["run_id"],
        "split": manifest["split"],
        "policy_hash": policy.sha256,
        "manifest_sha256": file_hash(run_dir / "manifest.json"),
        "expected_cases": len(questions) * len(methods),
        "completed_cases": len(rows),
        "methods": methods,
    }
    write_json(run_dir / "metrics.json", result)
    write_json(run_dir / "eligibility.json", eligibility_summary(questions, paragraphs, policy))
    return result


def run_evaluation(
    config,
    split,
    manifest,
    methods,
    *,
    qa=False,
    output=None,
    frozen_run_manifest=None,
    limit=None,
    interval_seconds=12,
    service=None,
):
    """Run all selected cases, checkpoint each result, and resume without re-querying.

    A quota error is retained and stops dispatch; remaining cases stay missing.
    Provider errors are never silently retried or reclassified as abstentions.
    """
    if config.top_k != 5:
        raise ValueError("This scoring policy requires top_k=5")
    if (
        not methods
        or len(set(methods)) != len(methods)
        or not set(methods) <= {"bm25", "dense", "hybrid"}
    ):
        raise ValueError("Choose unique supported retrieval methods")
    if split == "test":
        if frozen_run_manifest is None:
            raise ValueError("Final test requires a frozen run manifest")
        if (
            manifest is None
            or manifest.resolve() != (config.manifest_dir / "test_pilot.json").resolve()
        ):
            raise ValueError("Final test requires the explicit saved test_pilot manifest")
        if methods != [config.retrieval_method]:
            raise ValueError("Final test method must match the frozen candidate")
        validate_frozen_run(config, frozen_run_manifest)
    if interval_seconds < 0:
        raise ValueError("Request interval must be nonnegative")
    manifest = (
        manifest
        or config.manifest_dir / f"{'debug' if split == 'train' else split + '_pilot'}.json"
    )
    questions = load_cases(config, split, manifest, limit)
    binding = {
        "snapshot": snapshot(config),
        "selection_hash": file_hash(manifest),
        "question_ids": [q.question_id for q in questions],
        "methods": methods,
        "qa": qa,
        "split": split,
    }
    binding_hash = _hash(binding)
    output = output or config.report_dir / "runs" / f"eval-{split}-{uuid4().hex[:12]}"
    output.mkdir(parents=True, exist_ok=True)
    path = output / "manifest.json"
    if path.exists():
        saved = json.loads(path.read_text("utf-8"))
        if saved["sha256"] != binding_hash or saved["binding"] != binding:
            raise ValueError("Resume settings differ from the saved evaluation manifest")
    else:
        saved = {
            "run_id": output.name,
            "created_at": datetime.now(UTC).isoformat(),
            "sha256": binding_hash,
            "binding": binding,
            "split": split,
            "qa": qa,
            "methods": methods,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cold_startup_ms": None,
        }
        write_json(path, saved)
        write_jsonl(output / "references.jsonl", questions)
        paper_ids = {q.paper_id for q in questions}
        write_jsonl(
            output / "paragraphs.jsonl",
            [p for p in list_paragraphs(config.database_path) if p.paper_id in paper_ids],
        )
        saved["scoring_identity"] = scoring_identity()
        saved["scoring_input_hashes"] = {
            name: file_hash(output / name) for name in ("references.jsonl", "paragraphs.jsonl")
        }
        write_json(path, saved)
    if split == "test":
        # A frozen candidate gets one test evaluation directory; resume it after interruption.
        marker = config.manifest_dir / "test_pilot.consumed.json"
        if marker.exists():
            if json.loads(marker.read_text("utf-8"))["output"] != str(output.resolve()):
                raise ValueError(
                    "Final test was already started; resume its original output directory"
                )
        else:
            write_json(marker, {"output": str(output.resolve()), "manifest_sha256": binding_hash})
    prediction_path = output / "predictions.jsonl"
    rows = read_jsonl(prediction_path) if prediction_path.exists() else []
    completed = {(r["question_id"], r["method"]) for r in rows}
    if len(completed) != len(rows):
        raise ValueError("Duplicate saved predictions")
    remaining = [(q, m) for q in questions for m in methods if (q.question_id, m) not in completed]
    if not remaining:
        return report_run(output)
    started = time.perf_counter()
    if service is None:
        from evidence_assistant.generation_tokens import GenerationCounter
        from evidence_assistant.retrieval import RetrievalIndex
        from evidence_assistant.service import build_answer_service

        if qa:
            service = build_answer_service(config, "hybrid" if len(methods) > 1 else methods[0])
        else:
            service = AnswerService(
                config,
                RetrievalIndex.load(config, method="hybrid"),
                GenerationCounter.load(config),
                None,
            )
    service.purpose = "offline_evaluation"
    startup = (time.perf_counter() - started) * 1000
    if saved["cold_startup_ms"] is None:
        saved["cold_startup_ms"] = startup
        write_json(path, saved)
    previous_call = None
    for q, method in remaining:
        if qa:
            if previous_call is not None:
                time.sleep(max(0, interval_seconds - (time.monotonic() - previous_call)))
            previous_call = time.monotonic()
            try:
                answer = answer_question(q.question, q.paper_id, method, service)
                request_id = answer.request_id
            except ProviderError as exc:
                request_id = exc.request_id
            record = json.loads(
                (config.report_dir / "runs" / f"{request_id}.json").read_text("utf-8")
            )
            row = _enrich_record(q, record, config)
        else:
            row = _context_record(q, method, service)
        # Atomic rewrite is small for a pilot and avoids partial JSONL lines on interruption.
        rows.append(row)
        write_jsonl(prediction_path.with_suffix(".tmp"), rows)
        prediction_path.with_suffix(".tmp").replace(prediction_path)
        saved["prediction_sha256"] = file_hash(prediction_path)
        write_json(path, saved)
        print(
            f"{output.name}: {len(rows)}/{len(questions) * len(methods)} {method} {row['status']}",
            flush=True,
        )
        if row.get("error_code") == "rate_limited":
            break
    return report_run(output)
