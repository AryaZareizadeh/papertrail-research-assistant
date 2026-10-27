"""Streamlit interaction checks with synthetic API responses, never model calls."""

import hashlib
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from evidence_assistant import ui_client
from evidence_assistant.schemas import AnswerResult, Citation, DraftClaim, Paragraph


@pytest.fixture
def app_setup(monkeypatch):
    state = {"calls": 0, "mode": "answer"}
    text = "Dataset Alpha & surrounding <context>."
    source = Paragraph(
        paper_id="paper1",
        paragraph_id="p1",
        section_index=0,
        section_name="Methods",
        paragraph_index=0,
        text=text,
        text_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )

    class FakeAPI:
        def __init__(self, *args, **kwargs):
            pass

        def papers(self):
            return [
                ui_client.PaperInfo(paper_id=p, title=title, sections=[])
                for p, title in [("paper1", "A study of evidence"), ("paper2", "Another paper")]
            ]

        def ready(self):
            return {"status": "ready"}

        def ask(self, paper_id, question):
            state["calls"] += 1
            if state["mode"] == "error":
                raise ui_client.UIError("The model service is rate limited.", code="rate_limited")
            answered = state["mode"] == "answer"
            return AnswerResult(
                request_id="a" * 32,
                paper_id=paper_id,
                status="answered" if answered else "insufficient_evidence",
                claims=[DraftClaim(text="The study uses Dataset Alpha.", citation_chunk_ids=["c1"])]
                if answered
                else [],
                citations=[
                    Citation(
                        chunk_id="c1",
                        paper_id=paper_id,
                        paragraph_id="p1",
                        section_name="Methods",
                        start_char=0,
                        end_char=13,
                        quote="Dataset Alpha",
                    )
                ]
                if answered
                else [],
                retrieved_chunk_ids=["c1"],
                method="dense",
                model_id="synthetic",
                prompt_version="test",
                index_version="test",
                latency_ms=1250,
            )

        def paragraph(self, *args):
            return source

    monkeypatch.setattr(ui_client, "ApiClient", FakeAPI)
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "src/evidence_assistant/ui.py",
        default_timeout=10,
    )
    return app, state


def submit(app):
    app.run()
    assert not app.exception
    app.text_area[0].set_value("Which dataset?")
    next(b for b in app.button if b.label == "Ask about this paper").click().run()
    assert not app.exception


def test_question_citation_and_paper_change_do_not_regenerate(app_setup):
    app, state = app_setup
    submit(app)
    assert any("Dataset Alpha" in t.value for t in app.text)
    assert any("<mark>Dataset Alpha</mark>" in m.value for m in app.markdown)
    assert any("&lt;context&gt;" in m.value for m in app.markdown)
    next(b for b in app.button if b.label.startswith("Source 1")).click().run()
    assert state["calls"] == 1
    app.selectbox[0].select("paper2").run()
    assert not app.exception
    assert not any("The study uses Dataset Alpha" in t.value for t in app.text)
    assert state["calls"] == 1


@pytest.mark.parametrize("mode", ["refusal", "error"])
def test_insufficient_evidence_and_service_error_are_distinct(app_setup, mode):
    app, state = app_setup
    state["mode"] = mode
    submit(app)
    if mode == "refusal":
        assert any("sufficient evidence" in message.value for message in app.info)
        assert not app.error
    else:
        assert any("rate limited" in message.value for message in app.error)
        assert not any("sufficient evidence" in message.value for message in app.info)
