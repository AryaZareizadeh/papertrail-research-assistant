"""PaperTrail command-line interface; heavy model imports stay lazy."""

import argparse
import json
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from pydantic import ValidationError

from evidence_assistant.config import AppConfig, load_config


def doctor(config: AppConfig) -> dict:
    packages = {}
    for package in (
        "numpy",
        "rank-bm25",
        "sentence-transformers",
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "pyyaml",
        "streamlit",
        "pytest",
        "ruff",
    ):
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            packages[package] = "not installed"
    vector_file = "embeddings.npy"
    index_path = config.artifact_dir / "index_manifest.json"
    if index_path.is_file():
        vector_file = json.loads(index_path.read_text("utf-8")).get("vector_file", vector_file)
    artifacts = {
        "database": config.database_path,
        "embeddings": config.artifact_dir / vector_file,
        "index_manifest": config.artifact_dir / "index_manifest.json",
    }
    return {
        "python": platform.python_version(),
        "packages": packages,
        "paths": {k: str(v) for k, v in config if k.endswith("_dir")},
        "embedding": {"model": config.embedding_model, "revision": config.embedding_revision},
        "generation": {
            "model": config.generation_model,
            "digest": config.generation_digest,
            "tokenizer": config.generation_tokenizer,
            "ready": False,
            "note": "Readiness needs a model/tokenizer smoke test; doctor makes no network calls.",
        },
        "artifacts": {k: {"path": str(v), "exists": v.is_file()} for k, v in artifacts.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PaperTrail: research answers with source evidence"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("doctor", help="Inspect local setup without downloading anything")
    check.add_argument("--config", type=Path, default=Path("config.yaml"))
    descriptions = {
        "download": "Download the official QASPER archives",
        "normalize": "Separate runtime paper text from benchmark annotations",
        "prepare-tokenizer": "Download and pin the small embedding tokenizer",
        "prepare-embedding": "Download and pin the full embedding model",
        "prepare-generation-tokenizer": "Download and pin only the hosted model tokenizer",
        "calibrate-generation": "Verify hosted prompt token counts using training papers",
        "chunk": "Build source-preserving chunks and SQLite storage",
        "index": "Build dense embedding artifacts",
        "retrieve": "Find evidence in one selected paper",
        "answer": "Answer with hosted generation and stored source citations",
    }
    for name, description in descriptions.items():
        command = commands.add_parser(name, help=description)
        command.add_argument("--config", type=Path, default=Path("config.yaml"))
        if name == "chunk":
            command.add_argument(
                "--all-papers", action="store_true", help="Expand beyond pilot papers"
            )
        if name in {"retrieve", "answer"}:
            command.add_argument("--paper-id", required=True)
            command.add_argument("--question", required=True)
            command.add_argument("--method", choices=["bm25", "dense", "hybrid"])
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "doctor":
            result = doctor(config)
        elif args.command in {"prepare-embedding", "prepare-tokenizer"}:
            from evidence_assistant.embedding import prepare_embedding, prepare_tokenizer

            operation = (
                prepare_embedding if args.command == "prepare-embedding" else prepare_tokenizer
            )
            result = operation(config)
        elif args.command == "chunk":
            from evidence_assistant.embedding import load_tokenizer
            from evidence_assistant.pipeline import build_chunks

            result = build_chunks(config, load_tokenizer(config), all_papers=args.all_papers)
        elif args.command == "prepare-generation-tokenizer":
            from evidence_assistant.generation_tokens import prepare_generation_tokenizer

            result = prepare_generation_tokenizer(config)
        elif args.command == "calibrate-generation":
            from evidence_assistant.generation import ProviderError
            from evidence_assistant.generation_tokens import calibrate_generation

            try:
                result = calibrate_generation(config)
            except ProviderError as exc:
                print(f"Model service error: {exc}", file=sys.stderr)
                return 3
        elif args.command == "answer":
            from evidence_assistant.generation import ProviderError
            from evidence_assistant.service import answer_question, build_answer_service

            method = args.method or config.retrieval_method
            try:
                service = build_answer_service(config, method)
                result = answer_question(args.question, args.paper_id, method, service).model_dump()
            except ProviderError as exc:
                print(f"Model service error: {exc}", file=sys.stderr)
                return 3
        elif args.command == "index":
            from evidence_assistant.retrieval import build_index

            result = build_index(config.database_path, config.artifact_dir, config).model_dump()
        elif args.command == "retrieve":
            from time import perf_counter

            from evidence_assistant.retrieval import RetrievalIndex, retrieve

            method = args.method or config.retrieval_method
            index = RetrievalIndex.load(config, method=method)
            started = perf_counter()
            matches = retrieve(args.question, args.paper_id, method, config.top_k, index)
            result = {
                "matches": [match.model_dump() for match in matches],
                "retrieval_ms": (perf_counter() - started) * 1000,
                "includes_model_load": False,
            }
        else:
            from evidence_assistant.data import (
                download_qasper,
                normalize_release,
                read_jsonl,
                save_pilot_manifests,
            )

            if args.command == "download":
                result = download_qasper(config.raw_dir).model_dump()
            else:
                manifest = normalize_release(
                    config.raw_dir, config.corpus_dir, config.evaluation_dir
                )
                save_pilot_manifests(
                    manifest,
                    read_jsonl(config.corpus_dir / "papers.jsonl"),
                    config.manifest_dir,
                    config.seed,
                )
                result = manifest.model_dump()
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, ValidationError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
