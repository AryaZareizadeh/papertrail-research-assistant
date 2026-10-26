"""Pinned hosted-model tokenizer. Estimates remain separate from provider usage."""

import json
from datetime import UTC, datetime
from pathlib import Path

from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, text_hash, write_json


def prepare_generation_tokenizer(config: AppConfig) -> dict:
    from huggingface_hub import snapshot_download

    if not config.generation_model or not config.generation_tokenizer:
        raise ValueError("Configure a generation model and tokenizer first")
    snapshot = Path(
        snapshot_download(
            config.generation_tokenizer,
            revision=config.generation_tokenizer_revision,
            cache_dir=config.artifact_dir.parent / ".cache" / "huggingface",
            allow_patterns=[
                "tokenizer.json",
                "tokenizer_config.json",
                "chat_template.jinja",
                "special_tokens_map.json",
                "config.json",
            ],
        )
    )
    metadata = {
        "model": config.generation_model,
        "tokenizer": config.generation_tokenizer,
        "revision": snapshot.name,
        "snapshot": str(snapshot.resolve()),
        "file_hashes": {p.name: file_hash(p) for p in snapshot.iterdir() if p.is_file()},
        "provider_token_count_verified": False,
    }
    write_json(config.artifact_dir / "generation_tokenizer.json", metadata)
    return metadata


class GenerationCounter:
    def __init__(self, tokenizer, *, identity: str, prompt_offset: int = 0):
        self.tokenizer = tokenizer
        self.identity = identity
        self.prompt_offset = prompt_offset

    def count_text(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def count_prompt(self, messages: list[dict], schema: dict) -> int:
        ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=False,
            truncation=False,
            reasoning_effort="low",
        )
        # Provider schema/system overhead can differ; keep this explicitly estimated.
        return (
            len(ids) + self.count_text(json.dumps(schema, ensure_ascii=False)) + self.prompt_offset
        )

    @classmethod
    def load(cls, config: AppConfig, *, use_calibration: bool = True):
        from transformers import AutoTokenizer

        path = config.artifact_dir / "generation_tokenizer.json"
        if not path.is_file():
            raise ValueError("Run prepare-generation-tokenizer before answering")
        metadata = json.loads(path.read_text("utf-8"))
        if (
            metadata["model"] != config.generation_model
            or (metadata["tokenizer"] != config.generation_tokenizer)
            or (
                config.generation_tokenizer_revision
                and metadata["revision"] != config.generation_tokenizer_revision
            )
        ):
            raise ValueError("Prepared generation tokenizer differs from configuration")
        snapshot = Path(metadata["snapshot"])
        if any(
            file_hash(snapshot / name) != expected
            for name, expected in metadata["file_hashes"].items()
        ):
            raise ValueError("Generation tokenizer files changed; prepare them again")
        tokenizer = AutoTokenizer.from_pretrained(
            snapshot, local_files_only=True, trust_remote_code=False
        )
        identity = f"{metadata['tokenizer']}@{metadata['revision']}"
        calibration = config.artifact_dir / "generation_token_calibration.json"
        offset = 0
        if use_calibration and calibration.is_file():
            values = json.loads(calibration.read_text("utf-8"))
            if values["signature"] != counter_signature(config, metadata):
                raise ValueError("Token calibration differs from configuration; recalibrate")
            offset = values["prompt_offset"]
            if type(offset) is not int:
                raise ValueError("Invalid provider token calibration")
            identity += f":calibration-{file_hash(calibration)}"
        return cls(tokenizer, identity=identity, prompt_offset=offset)


def counter_signature(config: AppConfig, metadata: dict) -> str:
    from evidence_assistant.generation import ANSWER_SCHEMA, GENERATION_OPTIONS, SYSTEM_PROMPT

    return text_hash(
        json.dumps(
            {
                "endpoint": config.generation_endpoint,
                "model": config.generation_model,
                "tokenizer": metadata["tokenizer"],
                "revision": metadata["revision"],
                "tokenizer_file_hashes": metadata["file_hashes"],
                "prompt_version": config.prompt_version,
                "prompt": SYSTEM_PROMPT,
                "schema": ANSWER_SCHEMA,
                "options": GENERATION_OPTIONS,
            },
            sort_keys=True,
        )
    )


def infer_prompt_offset(samples: list[dict]) -> int:
    if len(samples) < 3:
        raise ValueError("At least three consistent provider measurements are required")
    differences = {s["actual"] - s["estimated"] for s in samples}
    if len(differences) != 1:
        raise ValueError("Provider token counts are not consistent with a fixed formatting offset")
    return differences.pop()


def calibrate_generation(config: AppConfig) -> dict:
    """Explicit live diagnostic using training papers only; never benchmark labels."""
    from evidence_assistant.service import answer_question, build_answer_service
    from evidence_assistant.store import list_papers

    service = build_answer_service(config, use_calibration=False)
    service.purpose = "token_calibration"
    papers = [p for p in list_papers(config.database_path) if p.split == "train"]
    if not papers:
        raise ValueError("Token calibration requires indexed training papers")
    questions = [
        "Which methods does this paper describe?",
        "Which data or evaluation metrics are described?",
        "Does this paper specify an annual marketing budget in dollars?",
    ]
    samples = []
    for i, question in enumerate(questions):
        result = answer_question(
            question, papers[i % len(papers)].paper_id, config.retrieval_method, service
        )
        run = json.loads(
            (config.report_dir / "runs" / f"{result.request_id}.json").read_text("utf-8")
        )
        if not run["attempts"]:
            raise ValueError("Calibration requires actual provider calls with supplied evidence")
        samples.append(
            {
                "request_id": result.request_id,
                "estimated": run["token_usage"]["input_tokens_estimated"],
                "actual": run["token_usage"]["input_tokens_actual"],
            }
        )
    offset = infer_prompt_offset(samples)
    service.counter.prompt_offset = offset
    service.counter.identity += f":candidate-offset-{offset}"
    validation = answer_question(
        "Which evaluation methods are described?",
        papers[0].paper_id,
        config.retrieval_method,
        service,
    )
    run = json.loads(
        (config.report_dir / "runs" / f"{validation.request_id}.json").read_text("utf-8")
    )
    if not run["token_usage"]["counter_verified"]:
        raise ValueError("Provider token calibration failed the independent validation prompt")
    metadata_path = config.artifact_dir / "generation_tokenizer.json"
    metadata = json.loads(metadata_path.read_text("utf-8"))
    calibration = {
        "created_at": datetime.now(UTC).isoformat(),
        "signature": counter_signature(config, metadata),
        "prompt_offset": offset,
        "samples": samples,
        "validation_request_id": validation.request_id,
        "validation_usage": run["token_usage"],
        "provider_fingerprint": run.get("provider_fingerprint"),
        "scope": "three training-paper probes plus one independent validation prompt",
    }
    write_json(config.artifact_dir / "generation_token_calibration.json", calibration)
    metadata["provider_token_count_verified"] = True
    write_json(metadata_path, metadata)
    return calibration
