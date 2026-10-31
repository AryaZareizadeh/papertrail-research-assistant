"""Human-facing preview/save workflow with fake API, never hosted inference."""

from evidence_assistant import ui_client
from evidence_assistant.library import ImportPreview, ImportSaved
from evidence_assistant.schemas import Paper
from tests.test_ui import app_setup as app_setup


def test_arxiv_preview_edit_save_select_and_no_generation(app_setup, monkeypatch):
    app, state = app_setup
    added = []
    cls = ui_client.ApiClient
    old_papers = cls.papers
    monkeypatch.setattr(cls, "papers", lambda self: old_papers(self) + added)
    def preview(self, url):
        state["preview_url"] = url
        return ImportPreview(preview_id="a" * 32, paper_id="pdf-" + "b" * 64,
                             title="Imported title", pages=2, text_pages=2,
                             preview_text="Readable extracted text.", preview_truncated=False,
                             origin=url, warnings=[])
    def confirm(self, preview_id, title):
        paper = Paper(paper_id="pdf-" + "b" * 64, split="user", title=title,
                      abstract="", source_revision="test")
        added.append(ui_client.PaperInfo(paper_id=paper.paper_id, title=title, sections=[]))
        state["saved_title"] = title
        return ImportSaved(paper=paper, already_exists=False)
    monkeypatch.setattr(cls, "preview_arxiv", preview, raising=False)
    monkeypatch.setattr(cls, "confirm_import", confirm, raising=False)
    app.run()
    assert not app.exception
    app.text_input(key="arxiv_input").set_value("https://arxiv.org/abs/2401.12345").run()
    next(b for b in app.button if b.label == "Preview arXiv paper").click().run()
    assert not app.exception
    assert "Readable extracted text." in app.code[0].value
    app.text_input(key="import_title").set_value("My chosen title")
    next(b for b in app.button if b.label == "Add to collection").click().run()
    assert not app.exception
    assert state["saved_title"] == "My chosen title"
    assert app.selectbox[0].value == "pdf-" + "b" * 64
    assert state["calls"] == 0
    assert "import_preview" not in app.session_state


def test_changing_import_input_clears_stale_preview(app_setup, monkeypatch):
    app, state = app_setup
    monkeypatch.setattr(ui_client.ApiClient, "preview_arxiv", lambda self, url: ImportPreview(
        preview_id="a" * 32, paper_id="pdf-" + "b" * 64, title="Old paper",
        pages=1, text_pages=1, preview_text="Old text", preview_truncated=False,
        origin=url, warnings=[]), raising=False)
    app.run()
    app.text_input(key="arxiv_input").set_value("2401.12345").run()
    next(b for b in app.button if b.label == "Preview arXiv paper").click().run()
    assert "import_preview" in app.session_state
    app.text_input(key="arxiv_input").set_value("2401.54321").run()
    assert "import_preview" not in app.session_state
    assert state["calls"] == 0
