"""Opt-in free Nemotron backend. The active Groq configuration is unchanged."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, text_hash, write_json
from evidence_assistant.generation import ANSWER_SCHEMA, GroqAdapter, ProviderError
from evidence_assistant.generation_tokens import GenerationCounter

MODEL_ID = "nvidia/nemotron-3-ultra-550b-a55b"
ENDPOINT = "https://router.requesty.ai/v1"
TOKENIZER = "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16"
REVISION = "77df655d5e9f8362164ed14dd8b48f8bce657498"


def candidate_config(config: AppConfig):
    return config.model_copy(
        update={
            "generation_model": MODEL_ID,
            "generation_endpoint": ENDPOINT,
            "generation_tokenizer": TOKENIZER,
            "generation_tokenizer_revision": REVISION,
            "generation_api_key_env": "REQUESTY_API_KEY",
        }
    )


def candidate_messages(messages, schema):
    result = [dict(m) for m in messages]
    instruction = (
        "\nReturn only a JSON object conforming to this schema, without markdown fences: "
        + json.dumps(schema, ensure_ascii=False)
    )
    if result and result[0]["role"] == "system":
        result[0]["content"] += instruction
    else:
        result.insert(0, {"role": "system", "content": instruction})
    return result


class RequestyAdapter(GroqAdapter):
    def __init__(self, config, *, client=None, catalog=None):
        if config.generation_api_key_env != "REQUESTY_API_KEY":
            raise ValueError("The Requesty backend requires REQUESTY_API_KEY")
        if (
            config.generation_model != MODEL_ID
            or config.generation_endpoint.rstrip("/") != ENDPOINT
        ):
            raise ValueError("Comparison requires the exact free NVIDIA model and endpoint")
        super().__init__(config, client=client)
        if catalog is None:
            try:
                reply = self.client.get(
                    ENDPOINT + "/models",
                    headers={"Authorization": f"Bearer {self._key}"},
                    timeout=config.timeout_seconds,
                )
                reply.raise_for_status()
                models = [m for m in reply.json()["data"] if m["id"] == MODEL_ID]
                if len(models) != 1:
                    raise ValueError("Exact free route unavailable")
                catalog = models[0]
            except Exception as exc:
                raise ProviderError(
                    "Cannot verify Requesty's free model catalog", code="catalog_unavailable"
                ) from exc
        prices = [catalog, *catalog.get("pricing", [])]
        if catalog.get("id") != MODEL_ID or any(
            p.get("input_price") != 0 or p.get("output_price") != 0 for p in prices
        ):
            raise ProviderError(
                "Exact NVIDIA route is not verified free", code="free_route_unavailable"
            )
        self.catalog = {
            k: catalog.get(k)
            for k in (
                "id",
                "input_price",
                "output_price",
                "pricing",
                "supports_output_json_object",
                "supports_output_json_schema",
            )
        }

    @property
    def request_settings(self):
        return {
            "temperature": 0,
            "stream": False,
            "max_tokens": self.config.max_output_tokens,
            "chat_template_kwargs": {"enable_thinking": False},
            "reasoning_effort": "none",
            "format_mode": "prompted-schema-v1",
        }

    def effective_messages(self, messages, schema):
        return candidate_messages(messages, schema)

    def accepted_models(self):
        return {MODEL_ID, MODEL_ID.split("/", 1)[1]}

    def payload(self, messages, schema):
        return {
            "model": MODEL_ID,
            "messages": candidate_messages(messages, schema),
            **{k: v for k, v in self.request_settings.items() if k != "format_mode"},
        }

    def generate(self, messages, schema):
        try:
            reply = super().generate(messages, schema)
        except ProviderError as exc:
            cost = exc.usage.get("cost_usd_actual")
            if cost is not None and cost != 0:
                raise ProviderError(
                    "Free route returned an unexpected nonzero cost",
                    code="unexpected_provider_cost",
                    attempts=exc.attempts,
                    attempt_log=exc.attempt_log,
                    usage=exc.usage,
                ) from exc
            raise
        if reply.cost_usd is not None and reply.cost_usd != 0:
            raise ProviderError(
                "Free route returned an unexpected nonzero cost",
                code="unexpected_provider_cost",
                attempts=reply.attempts,
                attempt_log=reply.attempt_log,
                usage={
                    "input_tokens_actual": reply.input_tokens,
                    "output_tokens_actual": reply.output_tokens,
                    "cost_usd_actual": reply.cost_usd,
                },
            )
        return reply


class RequestyCounter(GenerationCounter):
    def count_prompt(self, messages, schema):
        ids = self.tokenizer.apply_chat_template(
            candidate_messages(messages, schema),
            add_generation_prompt=True,
            tokenize=True,
            return_dict=False,
            truncation=False,
            enable_thinking=False,
        )
        return len(ids) + self.prompt_offset

    @classmethod
    def load(cls, config, *, use_calibration=True):
        from transformers import AutoTokenizer

        root = config.artifact_dir / "requesty"
        metadata = json.loads((root / "tokenizer_metadata.json").read_text("utf-8"))
        if metadata["revision"] != REVISION or metadata["tokenizer"] != TOKENIZER:
            raise ValueError("Prepared Nemotron tokenizer identity differs")
        snapshot = Path(metadata["snapshot"])
        if any(
            file_hash(snapshot / name) != digest for name, digest in metadata["file_hashes"].items()
        ):
            raise ValueError("Nemotron tokenizer files changed")
        offset, identity = 0, f"{TOKENIZER}@{REVISION}"
        path = root / "calibration.json"
        if use_calibration:
            values = json.loads(path.read_text("utf-8"))
            if values["signature"] != candidate_signature(config, metadata):
                raise ValueError("Nemotron token calibration differs; recalibrate")
            offset = values["prompt_offset"]
            if type(offset) is not int:
                raise ValueError("Invalid Nemotron prompt offset")
            identity += ":calibration-" + file_hash(path)
        tokenizer = AutoTokenizer.from_pretrained(
            snapshot, local_files_only=True, trust_remote_code=False
        )
        return cls(tokenizer, identity=identity, prompt_offset=offset)


def candidate_signature(config, metadata):
    from evidence_assistant.generation import SYSTEM_PROMPT

    return text_hash(
        json.dumps(
            {
                "model": MODEL_ID,
                "endpoint": ENDPOINT,
                "tokenizer": metadata,
                "effective_schema_prompt": candidate_messages(
                    [{"role": "system", "content": SYSTEM_PROMPT}], ANSWER_SCHEMA
                ),
                "request_options": {
                    "temperature": 0,
                    "stream": False,
                    "enable_thinking": False,
                    "reasoning_effort": "none",
                },
                "prompt_version": config.prompt_version,
            },
            sort_keys=True,
        )
    )


def prepare_candidate_tokenizer(config):
    from huggingface_hub import snapshot_download

    path = Path(
        snapshot_download(
            TOKENIZER,
            revision=REVISION,
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
        "tokenizer": TOKENIZER,
        "revision": REVISION,
        "snapshot": str(path.resolve()),
        "file_hashes": {p.name: file_hash(p) for p in path.iterdir() if p.is_file()},
    }
    write_json(config.artifact_dir / "requesty" / "tokenizer_metadata.json", metadata)
    return metadata


def build_candidate_service(config, *, use_calibration=True):
    from evidence_assistant.retrieval import RetrievalIndex
    from evidence_assistant.service import AnswerService

    candidate = candidate_config(config)
    return AnswerService(
        candidate,
        RetrievalIndex.load(config, method="hybrid"),
        RequestyCounter.load(candidate, use_calibration=use_calibration),
        RequestyAdapter(candidate),
    )


def calibrate_candidate(config, *, service=None, interval_seconds=15, reuse_cached=True):
    """Four explicit training-only probes, with safe reuse after quota interruption."""
    from evidence_assistant.generation import SYSTEM_PROMPT
    from evidence_assistant.generation_tokens import infer_prompt_offset
    from evidence_assistant.service import answer_question
    from evidence_assistant.store import list_chunks, list_papers

    if interval_seconds < 0:
        raise ValueError("Request interval must be nonnegative")
    service = service or build_candidate_service(config, use_calibration=False)
    candidate = candidate_config(config)
    if service.config != candidate:
        raise ValueError("Calibration service differs from the candidate configuration")
    service.purpose = "requesty_token_calibration"
    service.counter.prompt_offset = 0
    indexed = {c.paper_id for c in list_chunks(config.database_path)}
    papers = [
        p for p in list_papers(config.database_path) if p.split == "train" and p.paper_id in indexed
    ]
    if not papers:
        raise ValueError("Candidate calibration requires indexed training papers")
    questions = [
        "Which methods does this paper describe?",
        "Which data or evaluation metrics are described?",
        "Does this paper specify an annual marketing budget in dollars?",
        "Which evaluation methods are described?",
    ]
    source_hash = file_hash(config.database_path)
    prompt_hash = text_hash(SYSTEM_PROMPT + json.dumps(ANSWER_SCHEMA, sort_keys=True))
    old = []
    for path in (config.report_dir / "runs").glob("*.json"):
        value = json.loads(path.read_text("utf-8"))
        if not isinstance(value, dict):
            continue
        if (
            value.get("purpose") == service.purpose
            and value.get("status") in {"answered", "insufficient_evidence"}
            and value.get("configuration") == candidate.model_dump(mode="json")
            and value.get("source_hash") == source_hash
            and value.get("prompt_sha256") == prompt_hash
            and value.get("token_counter") == service.counter.identity
            and value.get("index_version") == service.index.index_version
            and value.get("requested_generation_options") == service.adapter.request_settings
        ):
            old.append(value)
    samples, previous, validation_id = [], None, None
    for i, question in enumerate(questions):
        paper_id = papers[i % len(papers)].paper_id
        reuse = [
            r
            for r in old
            if reuse_cached and i < 3 and r["question"] == question and r["paper_id"] == paper_id
        ]
        if reuse:
            record = reuse[0]
        else:
            if previous is not None:
                time.sleep(max(0, interval_seconds - (time.monotonic() - previous)))
            previous = time.monotonic()
            answer = answer_question(question, paper_id, "hybrid", service)
            record = json.loads(
                (candidate.report_dir / "runs" / f"{answer.request_id}.json").read_text("utf-8")
            )
        usage = record["token_usage"]
        if i < 3:
            samples.append(
                {
                    "request_id": record["request_id"],
                    "estimated": usage["input_tokens_estimated"],
                    "actual": usage["input_tokens_actual"],
                }
            )
            if len(samples) == 3:
                service.counter.prompt_offset = infer_prompt_offset(samples)
        else:
            if not usage["counter_verified"]:
                raise ValueError("Independent Nemotron token-count validation did not match")
            validation_id = record["request_id"]
    root = candidate.artifact_dir / "requesty"
    metadata = json.loads((root / "tokenizer_metadata.json").read_text("utf-8"))
    result = {
        "created_at": datetime.now(UTC).isoformat(),
        "signature": candidate_signature(candidate, metadata),
        "samples": samples,
        "prompt_offset": service.counter.prompt_offset,
        "validation_request_id": validation_id,
    }
    write_json(root / "calibration.json", result)
    return result
