import json

import httpx
import pytest

from evidence_assistant.comparison import run_comparison
from evidence_assistant.evaluation_runs import run_evaluation
from evidence_assistant.requesty import RequestyAdapter, candidate_config
from evidence_assistant.service import AnswerService
from tests.test_evaluation_runs import evaluation_setup as evaluation_setup
from tests.test_generation import (
    TestCounter,
    completion,
    make_service,
    model_response,
)
from tests.test_generation import (
    generation_setup as generation_setup,
)
from tests.test_requesty import MODEL_ID, catalog
from tests.test_retrieval import retrieval_setup as retrieval_setup


def test_comparison_reuses_exact_context_and_resumes_without_regeneration(
    evaluation_setup, tmp_path, monkeypatch
):
    config, index = evaluation_setup
    baseline, output = tmp_path / "baseline", tmp_path / "comparison"
    service = make_service((config, index), lambda req: model_response(completion()))
    run_evaluation(
        config,
        "train",
        config.manifest_dir / "validation_pilot.json",
        ["hybrid"],
        qa=True,
        output=baseline,
        service=service,
        interval_seconds=0,
    )
    calls = []

    def handler(req):
        calls.append(json.loads(req.content))
        body = model_response(completion()).json()
        body["model"], body["usage"]["cost"] = MODEL_ID, 0
        return httpx.Response(200, json=body)

    monkeypatch.setenv("REQUESTY_API_KEY", "synthetic-requesty-secret")
    candidate = candidate_config(config)
    service = AnswerService(
        candidate,
        index,
        TestCounter(),
        RequestyAdapter(
            candidate,
            catalog=catalog(),
            client=httpx.Client(transport=httpx.MockTransport(handler)),
        ),
    )
    monkeypatch.setattr(
        "evidence_assistant.service.retrieve",
        lambda *args: pytest.fail("A fixed-context comparison must not retrieve again"),
    )
    result = run_comparison(config, baseline, output, service=service, interval_seconds=0)
    assert len(calls) == 1
    old = json.loads((baseline / "predictions.jsonl").read_text())
    new = json.loads((output / "predictions.jsonl").read_text())
    assert new["supplied_passages"] == old["supplied_passages"]
    assert new["baseline_request_id"] == old["request_id"]
    assert result["paired_cases"] == 1
    run_comparison(config, baseline, output, service=service, interval_seconds=0)
    assert len(calls) == 1
    with pytest.raises(ValueError, match="differ|control"):
        run_comparison(
            config.model_copy(update={"max_output_tokens": 513}),
            baseline,
            output,
            service=service,
            interval_seconds=0,
        )
    path = baseline / "predictions.jsonl"
    path.write_text(path.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        run_comparison(config, baseline, tmp_path / "tampered", service=service, interval_seconds=0)


def test_interrupted_manifest_publication_recovers_completed_call(
    evaluation_setup, tmp_path, monkeypatch
):
    from evidence_assistant import comparison

    config, index = evaluation_setup
    baseline, output = tmp_path / "baseline", tmp_path / "interrupted"
    run_evaluation(
        config,
        "train",
        config.manifest_dir / "validation_pilot.json",
        ["hybrid"],
        qa=True,
        output=baseline,
        service=make_service((config, index), lambda req: model_response(completion())),
        interval_seconds=0,
    )
    calls = []

    def handler(req):
        calls.append(req)
        body = model_response(completion()).json()
        body["model"], body["usage"]["cost"] = MODEL_ID, 0
        return httpx.Response(200, json=body)

    monkeypatch.setenv("REQUESTY_API_KEY", "synthetic-requesty-secret")
    candidate = candidate_config(config)
    service = AnswerService(
        candidate,
        index,
        TestCounter(),
        RequestyAdapter(
            candidate,
            catalog=catalog(),
            client=httpx.Client(transport=httpx.MockTransport(handler)),
        ),
    )
    original_write = comparison.write_json

    def fail_manifest(path, value):
        if "manifest.json" in path.name and value.get("prediction_sha256"):
            raise OSError("injected failure after prediction publication")
        return original_write(path, value)

    monkeypatch.setattr(comparison, "write_json", fail_manifest)
    with pytest.raises(OSError, match="injected"):
        run_comparison(config, baseline, output, service=service, interval_seconds=0)
    assert len(calls) == 1
    monkeypatch.setattr(comparison, "write_json", original_write)
    result = run_comparison(config, baseline, output, service=service, interval_seconds=0)
    assert len(calls) == 1
    assert result["paired_cases"] == 1
