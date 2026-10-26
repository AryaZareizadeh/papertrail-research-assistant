import json

import httpx
import pytest

from evidence_assistant.generation import ANSWER_SCHEMA, ProviderError, parse_draft
from evidence_assistant.requesty import (
    MODEL_ID,
    RequestyAdapter,
    RequestyCounter,
    candidate_config,
    candidate_messages,
    candidate_signature,
)
from tests.test_evaluation_runs import evaluation_setup as evaluation_setup
from tests.test_generation import generation_setup as generation_setup
from tests.test_generation import model_response
from tests.test_retrieval import retrieval_setup as retrieval_setup


def catalog(price=0):
    return {
        "id": MODEL_ID,
        "input_price": price,
        "output_price": 0,
        "pricing": [{"input_price": price, "output_price": 0}],
        "supports_output_json_schema": False,
        "supports_output_json_object": False,
    }


def test_exact_free_route_and_prompted_schema_preserve_question_and_evidence(
    generation_setup, monkeypatch
):
    config, _ = generation_setup
    monkeypatch.setenv("REQUESTY_API_KEY", "synthetic-requesty-secret")
    captured = []

    def handler(req):
        captured.append(json.loads(req.content))
        body = model_response({"status": "insufficient_evidence", "claims": []}).json()
        body["model"] = "nemotron-3-ultra-550b-a55b"
        body["usage"]["cost"] = 0
        return httpx.Response(200, json=body)

    adapter = RequestyAdapter(
        candidate_config(config),
        catalog=catalog(),
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    messages = [
        {"role": "system", "content": "Evidence only"},
        {"role": "user", "content": '{"question":"Q","evidence":["verbatim"]}'},
    ]
    reply = adapter.generate(messages, ANSWER_SCHEMA)
    payload = captured[0]
    assert payload["model"] == MODEL_ID
    assert payload["messages"][1] == messages[1]
    assert payload["messages"] == candidate_messages(messages, ANSWER_SCHEMA)
    assert "response_format" not in payload
    assert payload["reasoning_effort"] == "none"
    assert "tools" not in payload and "requesty" not in payload
    assert payload["chat_template_kwargs"] == {"enable_thinking": False}
    assert payload["max_tokens"] == 512
    assert reply.cost_usd == 0
    assert parse_draft(reply.content).status == "insufficient_evidence"
    assert messages[0]["content"] == "Evidence only"


def test_catalog_price_increase_is_rejected_before_any_generation(generation_setup, monkeypatch):
    config, _ = generation_setup
    monkeypatch.setenv("REQUESTY_API_KEY", "synthetic-requesty-secret")
    with pytest.raises(ProviderError, match="free"):
        RequestyAdapter(candidate_config(config), catalog=catalog(price=0.001))
    with pytest.raises(ValueError, match="exact"):
        RequestyAdapter(
            candidate_config(config).model_copy(
                update={"generation_model": "nemotron-3-ultra-550b-a55b"}
            ),
            catalog=catalog(),
        )


def test_candidate_counter_counts_the_same_effective_messages_and_native_template():
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs):
            assert kwargs["enable_thinking"] is False
            assert kwargs["return_dict"] is False
            assert "reasoning_effort" not in kwargs
            assert "properties" in messages[0]["content"]
            return list(range(123))

    counter = RequestyCounter(Tokenizer(), identity="synthetic", prompt_offset=-2)
    assert counter.count_prompt([{"role": "system", "content": "Prompt"}], ANSWER_SCHEMA) == 121


def test_unexpected_nonzero_cost_is_error_with_known_usage(generation_setup, monkeypatch):
    config, _ = generation_setup
    monkeypatch.setenv("REQUESTY_API_KEY", "synthetic-requesty-secret")
    body = model_response({"status": "insufficient_evidence", "claims": []}).json()
    body["model"], body["usage"]["cost"] = MODEL_ID, 0.01
    adapter = RequestyAdapter(
        candidate_config(config),
        catalog=catalog(),
        client=httpx.Client(
            transport=httpx.MockTransport(lambda req: httpx.Response(200, json=body))
        ),
    )
    with pytest.raises(ProviderError) as error:
        adapter.generate([], ANSWER_SCHEMA)
    assert error.value.code == "unexpected_provider_cost"
    assert error.value.usage["cost_usd_actual"] == 0.01
    assert error.value.usage["input_tokens_actual"] == 100


def test_nonzero_cost_on_truncated_output_still_stops_further_dispatch(
    generation_setup, monkeypatch
):
    config, _ = generation_setup
    monkeypatch.setenv("REQUESTY_API_KEY", "synthetic-requesty-secret")
    body = model_response({"status": "answered", "claims": []}).json()
    body["model"], body["usage"]["cost"] = MODEL_ID, 0.01
    body["choices"][0]["finish_reason"] = "length"
    adapter = RequestyAdapter(
        candidate_config(config),
        catalog=catalog(),
        client=httpx.Client(
            transport=httpx.MockTransport(lambda req: httpx.Response(200, json=body))
        ),
    )
    with pytest.raises(ProviderError) as error:
        adapter.generate([], ANSWER_SCHEMA)
    assert error.value.code == "unexpected_provider_cost"
    assert error.value.usage["cost_usd_actual"] == 0.01


def test_candidate_calibration_signature_binds_common_prompt(generation_setup, monkeypatch):
    config, _ = generation_setup
    before = candidate_signature(config, {"tokenizer": "synthetic"})
    monkeypatch.setattr(
        "evidence_assistant.generation.SYSTEM_PROMPT", "Changed source instructions"
    )
    assert candidate_signature(config, {"tokenizer": "synthetic"}) != before


def test_requesty_rejects_a_groq_key_variable_before_reading_any_key(generation_setup):
    config, _ = generation_setup
    wrong = candidate_config(config).model_copy(update={"generation_api_key_env": "GROQ_API_KEY"})
    with pytest.raises(ValueError, match="REQUESTY_API_KEY"):
        RequestyAdapter(wrong, catalog=catalog())


def test_candidate_calibration_requires_three_consistent_probes_and_independent_check(
    evaluation_setup, monkeypatch
):
    from types import SimpleNamespace

    from evidence_assistant import requesty
    from evidence_assistant.generation import ProviderReply
    from evidence_assistant.service import AnswerService
    from tests.test_generation import TestCounter, completion

    base, index = evaluation_setup
    config = candidate_config(base)
    root = config.artifact_dir / "requesty"
    root.mkdir()
    metadata = {"tokenizer": "synthetic", "revision": "synthetic", "file_hashes": {}}
    (root / "tokenizer_metadata.json").write_text(json.dumps(metadata))

    class Counter(TestCounter):
        prompt_offset = 0

        def count_prompt(self, messages, schema):
            return super().count_prompt(messages, schema) + self.prompt_offset

    calls = []
    provider_offset = [3]

    def generate(messages, schema):
        calls.append(messages)
        evidence = json.loads(messages[1]["content"])["evidence"]
        return ProviderReply(
            content=json.dumps(completion([evidence[0]["chunk_id"]])),
            model_id=MODEL_ID,
            fingerprint="synthetic",
            input_tokens=TestCounter().count_prompt(messages, schema) + provider_offset[0],
            output_tokens=60,
            attempts=1,
            attempt_log=[],
            cost_usd=0,
        )

    adapter = SimpleNamespace(generate=generate, request_settings={"synthetic": True})
    service = AnswerService(config, index, Counter(), adapter)
    result = requesty.calibrate_candidate(base, service=service, interval_seconds=0)
    assert len(calls) == 4
    assert result["prompt_offset"] == 3
    assert len(result["samples"]) == 3
    assert result["signature"] == candidate_signature(config, metadata)
    record = json.loads(
        (config.report_dir / "runs" / (result["validation_request_id"] + ".json")).read_text()
    )
    assert record["token_usage"]["counter_verified"]
    provider_offset[0] = 4
    with pytest.raises(ValueError, match="Independent"):
        requesty.calibrate_candidate(base, service=service, interval_seconds=0)
    fresh = requesty.calibrate_candidate(
        base, service=service, interval_seconds=0, reuse_cached=False
    )
    assert fresh["prompt_offset"] == 4
    assert len(calls) == 9


@pytest.mark.parametrize(
    "command", ["prepare-candidate-tokenizer", "calibrate-candidate", "compare-models"]
)
def test_candidate_cli_commands_use_explicit_opt_in_without_changing_config(
    tmp_path, monkeypatch, command
):
    from evidence_assistant.cli import main

    config_path = tmp_path / "config.yaml"
    config_path.write_text("{}", encoding="utf-8")
    calls = []

    def operation(config, *args, **kwargs):
        calls.append((config, args, kwargs))
        return {"command": command}

    function = {
        "prepare-candidate-tokenizer": "evidence_assistant.requesty.prepare_candidate_tokenizer",
        "calibrate-candidate": "evidence_assistant.requesty.calibrate_candidate",
        "compare-models": "evidence_assistant.comparison.run_comparison",
    }[command]
    monkeypatch.setattr(function, operation)
    argv = [command, "--config", str(config_path)]
    if command == "compare-models":
        argv += [
            "--source-run-dir",
            str(tmp_path / "baseline"),
            "--output",
            str(tmp_path / "candidate"),
        ]
    assert main(argv) == 0
    assert len(calls) == 1
    assert calls[0][0].generation_model is None
    assert config_path.read_text() == "{}"
