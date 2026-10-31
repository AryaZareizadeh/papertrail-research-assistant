"""Full preview/save/answer HTTP flow with synthetic PDF and model responses."""

import httpx
import pytest
from fastapi.testclient import TestClient

from evidence_assistant import library as library_module
from evidence_assistant.api import create_app
from evidence_assistant.data import file_hash
from evidence_assistant.store import list_chunks
from evidence_assistant.ui_client import ApiClient, UIError
from tests.test_api import api_setup as api_setup
from tests.test_generation import completion, model_response
from tests.test_generation import generation_setup as generation_setup
from tests.test_paper_import import pdf_bytes
from tests.test_retrieval import retrieval_setup as retrieval_setup


def test_upload_preview_confirm_select_answer_and_restart(api_setup):
    client, service, state, config = api_setup
    before = file_hash(config.database_path)
    ui = ApiClient("http://testserver", transport=client)
    preview = ui.preview_pdf(pdf_bytes(), "../a.pdf")
    assert preview.pages == 1
    assert len(ui.papers()) == 3
    saved = ui.confirm_import(preview.preview_id, "Uploaded study")
    assert saved.paper.title == "Uploaded study"
    assert len(ui.papers()) == 4
    assert state["provider_calls"] == 0
    assert ui.confirm_import(preview.preview_id, "Repeat").already_exists
    paper_id = saved.paper.paper_id
    cid = list_chunks(config.library_path / paper_id / "corpus.sqlite")[0].chunk_id
    service.adapter.client = httpx.Client(transport=httpx.MockTransport(
        lambda request: model_response(completion(claim_ids=[cid]))
    ))
    answer = ui.ask(paper_id, "Which dataset?")
    source = ui.paragraph(paper_id, answer.citations[0].paragraph_id)
    assert answer.citations[0].quote in source.text
    assert file_hash(config.database_path) == before
    app = create_app(config=config, service_factory=lambda settings: service)
    with TestClient(app) as restarted:
        assert paper_id in {p["paper_id"] for p in restarted.get("/papers").json()}


def test_arxiv_preview_uses_same_save_flow(api_setup, monkeypatch):
    client, service, state, _ = api_setup
    monkeypatch.setattr(library_module, "fetch_arxiv", lambda value: (
        pdf_bytes(), "https://arxiv.org/abs/2401.12345"
    ))
    ui = ApiClient("http://testserver", transport=client)
    preview = ui.preview_arxiv("https://arxiv.org/abs/2401.12345")
    assert preview.origin == "https://arxiv.org/abs/2401.12345"
    assert ui.confirm_import(preview.preview_id, preview.title).paper.paper_id == preview.paper_id
    assert state["provider_calls"] == 0


def test_import_errors_have_actionable_ui_messages(api_setup):
    client, _, _, _ = api_setup
    ui = ApiClient("http://testserver", transport=client)
    with pytest.raises(UIError, match="PDF"):
        ui.preview_pdf(b"bad", "not.pdf")
    with pytest.raises(UIError, match="preview"):
        ui.confirm_import("a" * 32, "Title")
    assert client.post("/imports/arxiv", json={"url": "https://evil.test/x"}).status_code == 422


def test_oversized_upload_stops_before_parsing(api_setup, monkeypatch):
    from evidence_assistant import api
    client, _, _, _ = api_setup
    monkeypatch.setattr(api, "MAX_PDF_BYTES", 10)
    response = client.post("/imports/pdf", content=b"x" * 11,
                           headers={"content-type": "application/pdf"})
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "pdf_too_large"
