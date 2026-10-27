"""API mechanics use synthetic model responses; this is not a quality benchmark."""

import json
import sqlite3

import httpx
import pytest
from fastapi.testclient import TestClient

from evidence_assistant import api
from evidence_assistant import service as service_module
from evidence_assistant.api import create_app
from evidence_assistant.generation import ProviderError
from evidence_assistant.service import answer_question
from tests.test_generation import (
    completion,
    make_service,
    model_response,
)
from tests.test_generation import (
    generation_setup as generation_setup,
)
from tests.test_retrieval import retrieval_setup as retrieval_setup


@pytest.fixture
def api_setup(generation_setup):
    config, index = generation_setup
    config = config.model_copy(update={"retrieval_method": "dense"})
    state = {"mode": "answered", "provider_calls": 0, "factory_calls": 0}

    def handler(request):
        state["provider_calls"] += 1
        if state["mode"] == "timeout":
            raise httpx.ReadTimeout("synthetic timeout", request=request)
        if state["mode"] == "invalid":
            return model_response("not JSON")
        if state["mode"] == "rate_limit":
            return httpx.Response(429, headers={"Retry-After": "20"})
        return model_response(
            completion(status="insufficient_evidence" if state["mode"] == "refusal" else "answered")
        )

    service = make_service((config, index), handler)

    def factory(settings):
        assert settings == config
        state["factory_calls"] += 1
        return service

    app = create_app(config=config, service_factory=factory)
    with TestClient(app) as client:
        yield client, service, state, config


def test_answer_reuses_offline_pipeline_and_request_id(api_setup, caplog):
    client, service, state, config = api_setup
    offline = answer_question("Which dataset?", "selected", "dense", service)
    with caplog.at_level("INFO", logger="evidence_assistant.api"):
        response = client.post(
            "/questions", json={"paper_id": "selected", "question": "Which dataset?"}
        )
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == "dense"
    assert {
        k: v for k, v in result.items() if k not in {"request_id", "latency_ms"}
    } == offline.model_dump(exclude={"request_id", "latency_ms"})
    assert response.headers["X-Request-ID"] == result["request_id"]
    assert result["request_id"] in caplog.text
    assert "unit-test-secret" not in response.text
    assert (config.report_dir / "runs" / (result["request_id"] + ".json")).exists()
    assert state["factory_calls"] == 1


def test_refusal_is_successful_empty_answer_not_service_error(api_setup):
    client, _, state, _ = api_setup
    state["mode"] = "refusal"
    r = client.post(
        "/questions", json={"paper_id": "selected", "question": "An unsupported question?"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "insufficient_evidence"
    assert r.json()["claims"] == r.json()["citations"] == []


def test_health_ready_and_paper_source_metadata_do_not_generate(api_setup):
    client, _, state, _ = api_setup
    assert client.get("/health").json()["status"] == "alive"
    assert client.get("/ready").status_code == 200
    papers = client.get("/papers")
    assert papers.status_code == 200
    selected = next(p for p in papers.json() if p["paper_id"] == "selected")
    assert selected["title"] == "selected"
    assert selected["sections"] == [
        {"section_index": 0, "section_name": "Methods", "paragraph_count": 3}
    ]
    assert "references" not in selected and "qas" not in selected
    source = client.get("/papers/selected/paragraphs/selected:s0000:p0000")
    assert source.status_code == 200
    assert source.json()["text"] == "Dataset Alpha"
    assert state["factory_calls"] == 1 and state["provider_calls"] == 0


def test_unknown_paper_and_cross_paper_source_are_404(api_setup):
    client, _, state, _ = api_setup
    r = client.post("/questions", json={"paper_id": "missing", "question": "Which dataset?"})
    assert r.status_code == 404
    assert r.json()["detail"]["request_id"] == r.headers["X-Request-ID"]
    assert client.get("/papers/selected/paragraphs/other:s0000:p0000").status_code == 404
    assert client.get("/papers/missing/paragraphs/selected:s0000:p0000").status_code == 404
    assert state["provider_calls"] == 0


@pytest.mark.parametrize(
    "fields",
    [
        {"paper_id": "selected", "question": ""},
        {"paper_id": "selected", "question": "   "},
        {"paper_id": "selected", "question": "x" * 2001},
        {"paper_id": "selected", "question": "Which dataset?", "method": "bm25"},
        {"paper_id": "", "question": "Which dataset?"},
    ],
)
def test_invalid_fields_are_422_without_provider_call(api_setup, fields):
    client, _, state, _ = api_setup
    r = client.post("/questions", json=fields)
    assert r.status_code == 422
    assert r.json()["detail"]["request_id"] == r.headers["X-Request-ID"]
    assert state["provider_calls"] == 0


@pytest.mark.parametrize(
    "mode,status,code",
    [
        ("timeout", 503, "transport_error"),
        ("invalid", 502, "invalid_answer_json"),
        ("rate_limit", 503, "rate_limited"),
    ],
)
def test_provider_errors_are_distinct_safe_and_traceable(api_setup, mode, status, code):
    client, _, state, config = api_setup
    state["mode"] = mode
    r = client.post("/questions", json={"paper_id": "selected", "question": "Which dataset?"})
    assert r.status_code == status
    detail = r.json()["detail"]
    assert detail["code"] == code and detail["request_id"] == r.headers["X-Request-ID"]
    assert "Traceback" not in r.text and "unit-test-secret" not in r.text
    record = json.loads((config.report_dir / "runs" / (detail["request_id"] + ".json")).read_text())
    assert record["status"] == "error"
    if mode == "rate_limit":
        assert r.headers["Retry-After"] == "20"


def test_openapi_describes_the_actual_error_envelope(api_setup):
    client, _, _, _ = api_setup
    spec = client.get("/openapi.json").json()
    responses = spec["paths"]["/questions"]["post"]["responses"]
    for status in ["404", "422", "502", "503"]:
        assert responses[status]["content"]["application/json"]["schema"]["$ref"].endswith(
            "/ErrorResponse"
        )


def test_alive_is_not_ready_when_generation_dependency_missing(generation_setup):
    config, _ = generation_setup

    def unavailable(settings):
        raise ProviderError("SECRET_INTERNAL_DIAGNOSTIC", code="missing_api_key")

    with TestClient(create_app(config=config, service_factory=unavailable)) as client:
        assert client.get("/health").status_code == 200
        r = client.get("/ready")
        assert r.status_code == 503 and r.json()["detail"]["code"] == "missing_api_key"
        assert "SECRET_INTERNAL_DIAGNOSTIC" not in r.text
        assert client.get("/papers").status_code == 200
        question = client.post(
            "/questions", json={"paper_id": "selected", "question": "Which dataset?"}
        )
        assert question.status_code == 503
        assert "SECRET_INTERNAL_DIAGNOSTIC" not in question.text


@pytest.mark.parametrize("error", [OSError, sqlite3.OperationalError, ValueError, RuntimeError])
def test_core_errors_preserve_the_persisted_run_id(api_setup, monkeypatch, caplog, error):
    client, _, _, config = api_setup

    def fail(*args, **kwargs):
        raise error("SECRET_INTERNAL_DIAGNOSTIC")

    monkeypatch.setattr(service_module, "get_paper", fail)
    with caplog.at_level("INFO", logger="evidence_assistant.api"):
        response = client.post(
            "/questions", json={"paper_id": "selected", "question": "Which dataset?"}
        )
    assert response.status_code == (500 if error is RuntimeError else 503)
    saved = list((config.report_dir / "runs").glob("*.json"))
    assert len(saved) == 1
    record = json.loads(saved[0].read_text())
    assert record["request_id"] == response.json()["detail"]["request_id"]
    assert record["request_id"] == response.headers["X-Request-ID"]
    assert record["request_id"] in caplog.text
    assert "SECRET_INTERNAL_DIAGNOSTIC" not in response.text


def test_malformed_path_configuration_keeps_liveness_available(tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text("artifact_dir: null\n", encoding="utf-8")
    with TestClient(create_app(config_path=path)) as client:
        assert client.get("/health").status_code == 200
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "configuration_unavailable"


def test_bm25_readiness_does_not_require_dense_model_artifacts(generation_setup, monkeypatch):
    config, index = generation_setup
    config = config.model_copy(update={"retrieval_method": "bm25"})
    service = make_service((config, index), lambda _: model_response(completion()))
    for name in ("index_manifest.json", "embedding_model.json"):
        (config.artifact_dir / name).unlink(missing_ok=True)
    for name in ("generation_tokenizer.json", "generation_token_calibration.json"):
        (config.artifact_dir / name).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(api, "build_answer_service", lambda _: service)
    with TestClient(create_app(config=config)) as client:
        assert client.get("/ready").status_code == 200
