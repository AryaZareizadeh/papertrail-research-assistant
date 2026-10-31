"""Persistent imported papers must not change the benchmark corpus."""

from importlib import import_module

import httpx
import pytest

from evidence_assistant.data import file_hash
from evidence_assistant.retrieval import retrieve
from evidence_assistant.service import answer_question
from evidence_assistant.store import list_chunks
from tests.test_generation import generation_setup as generation_setup
from tests.test_generation import make_service, model_response
from tests.test_paper_import import pdf_bytes
from tests.test_retrieval import retrieval_setup as retrieval_setup


def test_library_preview_commit_restart_and_exact_citations(generation_setup):
    module = import_module("evidence_assistant.library")
    config, index = generation_setup
    service = make_service(generation_setup, lambda request: model_response({
        "status": "answered", "claims": [{
            "text": "Dataset Alpha uses accuracy.",
            "citation_chunk_ids": [request.extensions['citation_id']],
        }],
    }))
    before = file_hash(config.database_path)
    library = module.PaperLibrary(config)
    preview = library.preview(pdf_bytes(), filename="../../test.pdf")
    assert preview.preview_text == "Dataset Alpha uses accuracy."
    assert library.papers() == []
    saved = library.confirm(preview.preview_id, "My imported paper", service)
    assert saved.paper.title == "My imported paper"
    assert not saved.already_exists
    assert file_hash(config.database_path) == before
    assert library.confirm(preview.preview_id, "Duplicate title", service).already_exists
    restarted = module.PaperLibrary(config)
    assert restarted.papers()[0].paper_id == saved.paper.paper_id
    imported = restarted.service(saved.paper.paper_id, service)
    results = retrieve("Dataset?", saved.paper.paper_id, "dense", 5, imported.index)
    assert results and all(r.chunk.paper_id == saved.paper.paper_id for r in results)
    cid = results[0].chunk.chunk_id
    imported.adapter.client = httpx.Client(transport=httpx.MockTransport(
        lambda request: model_response({"status": "answered", "claims": [{
            "text": "Dataset Alpha uses accuracy.", "citation_chunk_ids": [cid]
        }]})
    ))
    answer = answer_question("Which dataset?", saved.paper.paper_id, "dense", imported)
    citation = answer.citations[0]
    source = restarted.paragraph(saved.paper.paper_id, citation.paragraph_id)
    assert source.text[citation.start_char:citation.end_char] == citation.quote
    assert citation.section_name == "Page 1"
    assert len(list_chunks(config.database_path)) == len(index.chunks)


def test_library_failed_embedding_publishes_nothing(generation_setup, monkeypatch):
    module = import_module("evidence_assistant.library")
    service = make_service(generation_setup, lambda request: model_response({}))
    library = module.PaperLibrary(service.config)
    preview = library.preview(pdf_bytes())
    def fail(*args, **kwargs):
        raise ValueError("synthetic embedding failure")
    monkeypatch.setattr(module, "build_index", fail)
    with pytest.raises(module.ImportProblem, match="save"):
        library.confirm(preview.preview_id, "A paper", service)
    assert library.papers() == []
    assert not list(library.root.glob("pdf-*"))


@pytest.mark.parametrize("token", ["../secret", "bad", "a" * 32])
def test_unknown_preview_is_rejected(generation_setup, token):
    module = import_module("evidence_assistant.library")
    service = make_service(generation_setup, lambda request: model_response({}))
    with pytest.raises(module.ImportProblem):
        module.PaperLibrary(service.config).confirm(token, "A paper", service)
