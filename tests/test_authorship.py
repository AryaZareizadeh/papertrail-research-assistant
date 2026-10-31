"""Imported front matter must reach authorship answers without rewriting sources."""

import json

import numpy as np
import pytest

from evidence_assistant.config import AppConfig
from evidence_assistant.generation import SYSTEM_PROMPT, build_messages
from evidence_assistant.retrieval import RetrievalIndex, retrieve
from evidence_assistant.schemas import Chunk, Paper
from evidence_assistant.service import prepare_context


def author_index():
    chunks = [Chunk(
        chunk_id=f"pdf-test:page{page:04d}:c0000", paragraph_id=f"pdf-test:page{page:04d}",
        paper_id="pdf-test", section_name=f"Page {page}", start_char=0, end_char=len(text),
        text=text, token_count=20, chunking_version="test",
    ) for page, text in [
        (1, 'Title\nA/r.sc/y.sc/a.sc Z/a.sc/r.sc/e.sc/i.sc/z.sc/a.sc/d.sc/e.sc/h.sc'
            'AND N/a.sc/j.sc/m.sc/e.sc/h.sc N/o.sc/z.sc/h.sc/a.sc/t.sc*\n*contact@example.org'),
        (5, 'Results and the main geometrical parameters.'),
        (6, 'The authors declare no conflicts of interest.'),
    ]]
    class Encoder:
        def encode(self, texts, **kwargs):
            return np.array([[0., 1.] for text in texts])
    return RetrievalIndex(chunks, {"pdf-test"}, np.array([[1., 0.], [0., 1.], [0., 1.]]),
                          Encoder(), AppConfig(), "test")


@pytest.mark.parametrize("question", [
    "who is the main author", "Who is the first author?", "Who are the authors?",
    "Who wrote this paper?", "Who is the corresponding author?", "List the authors.",
])
def test_imported_authorship_prioritizes_first_page(question):
    index = author_index()
    # The library enables the policy; base/frozen retrieval leaves it disabled.
    index.prefer_pdf_frontmatter = True
    results = retrieve(question, "pdf-test", "dense", 2, index)
    assert results[0].chunk.section_name == "Page 1"
    assert len(results) == 2 and len({r.chunk.chunk_id for r in results}) == 2


def test_substantive_author_question_and_benchmark_retrieval_are_unchanged():
    index = author_index()
    baseline = retrieve("who is the main author", "pdf-test", "dense", 2, index)
    assert baseline[0].chunk.section_name != "Page 1"
    index.prefer_pdf_frontmatter = True
    substantive = retrieve("What method do the authors propose?", "pdf-test", "dense", 2, index)
    assert substantive == baseline


def test_imported_authorship_prompt_preserves_original_and_decodes_small_caps():
    index = author_index()
    source = index.chunks[0]
    evidence = retrieve("question", "pdf-test", "bm25", 3, index)
    paper = Paper(paper_id="pdf-test", split="user", title="Title", abstract="",
                  source_revision="pdf-text-v1:test")
    messages = build_messages("who is the main author", paper, evidence)
    payload = json.loads(messages[1]["content"])
    record = next(r for r in payload["evidence"] if r["chunk_id"] == source.chunk_id)
    assert record["text"] == source.text
    assert "Arya Zareizadeh AND Najmeh Nozhat*" in record["readable_text"]
    assert "first-listed" in messages[0]["content"]
    assert "corresponding" in messages[0]["content"]
    assert "contribution" in messages[0]["content"]
    benchmark = build_messages("who is the main author", replace_paper(paper), evidence)
    assert benchmark[0]["content"] == SYSTEM_PROMPT
    assert all("readable_text" not in r for r in json.loads(benchmark[1]["content"])["evidence"])


def replace_paper(paper):
    return paper.model_copy(update={"split": "train"})


def test_readable_pdf_hints_count_toward_evidence_budget():
    from evidence_assistant.generation import evidence_records
    index = author_index()
    index.prefer_pdf_frontmatter = True
    retrieved = retrieve("who is the main author", "pdf-test", "dense", 1, index)
    raw_size = len(json.dumps(evidence_records(retrieved), ensure_ascii=False))
    config = index.config.model_copy(update={"max_evidence_tokens": raw_size + 5})
    paper = Paper(paper_id="pdf-test", split="user", title="Title", abstract="",
                  source_revision="pdf-text-v1:test")
    class Counter:
        def count_prompt(self, messages, schema):
            return 100
        def count_text(self, text):
            return len(text)
    supplied, _, _, _ = prepare_context(
        "who is the main author", paper, retrieved, config, Counter()
    )
    assert supplied == []
