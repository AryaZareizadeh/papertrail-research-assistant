import pytest

from evidence_assistant.chunking import chunk_paragraph
from evidence_assistant.config import AppConfig
from evidence_assistant.data import normalize_release, read_jsonl
from evidence_assistant.schemas import Paper, Paragraph
from evidence_assistant.store import build_store, get_chunk, get_paragraph, list_chunks, list_papers
from tests.helpers import OffsetTokenizer


@pytest.fixture
def records(qasper_release, tmp_path):
    corpus = tmp_path / "corpus"
    normalize_release(qasper_release, corpus, tmp_path / "gold")
    papers = [Paper(**p) for p in read_jsonl(corpus / "papers.jsonl")]
    paragraphs = [Paragraph(**p) for p in read_jsonl(corpus / "paragraphs.jsonl")]
    chunks = [c for p in paragraphs for c in chunk_paragraph(p, OffsetTokenizer(), AppConfig())]
    return papers, paragraphs, chunks


def test_store_roundtrip_preserves_duplicates_and_excludes_gold(records, tmp_path):
    papers, paragraphs, chunks = records
    database = tmp_path / "corpus.sqlite"
    build_store(papers, paragraphs, chunks, database)
    assert len(list_papers(database)) == 3
    assert len(list_chunks(database, "paper-train")) == 3
    chunk = chunks[1]
    assert get_chunk(database, chunk.chunk_id) == chunk
    assert get_paragraph(database, chunk.paper_id, chunk.paragraph_id).text == chunk.text
    assert get_paragraph(database, "other-paper", chunk.paragraph_id) is None
    assert b"GOLD_SECRET" not in database.read_bytes()


def test_invalid_source_span_does_not_replace_valid_store(records, tmp_path):
    papers, paragraphs, chunks = records
    database = tmp_path / "corpus.sqlite"
    build_store(papers, paragraphs, chunks, database)
    original = database.read_bytes()
    bad = chunks[0].model_copy(update={"text": "X" * len(chunks[0].text)})
    with pytest.raises(ValueError, match="source"):
        build_store(papers, paragraphs, [bad], database)
    assert database.read_bytes() == original


def test_wrong_paper_chunk_is_rejected(records, tmp_path):
    papers, paragraphs, chunks = records
    bad = chunks[0].model_copy(update={"paper_id": "paper-test"})
    with pytest.raises(ValueError, match="paper"):
        build_store(papers, paragraphs, [bad], tmp_path / "corpus.sqlite")


def test_misleading_section_name_is_rejected(records, tmp_path):
    papers, paragraphs, chunks = records
    bad = chunks[0].model_copy(update={"section_name": "Fabricated results"})
    with pytest.raises(ValueError, match="section"):
        build_store(papers, paragraphs, [bad], tmp_path / "corpus.sqlite")
