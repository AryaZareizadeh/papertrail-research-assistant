import pytest

from evidence_assistant.chunking import chunk_paragraph
from evidence_assistant.config import AppConfig
from evidence_assistant.data import text_hash
from evidence_assistant.schemas import Paragraph
from tests.helpers import OffsetTokenizer


@pytest.mark.parametrize(
    "text", ["short text", "", "   ", "αβ  中文  داده\nlast", "  " + "word " * 600 + "last  "]
)
def test_chunks_preserve_source_offsets_and_token_limit(text):
    paragraph = Paragraph(
        paragraph_id="p:s0000:p0000",
        paper_id="p",
        section_index=0,
        section_name="Methods",
        paragraph_index=0,
        text=text,
        text_sha256=text_hash(text),
    )
    tokenizer = OffsetTokenizer()
    chunks = chunk_paragraph(paragraph, tokenizer, AppConfig())
    if not text.strip():
        assert chunks == []
        return
    covered = set()
    for chunk in chunks:
        assert chunk.text == text[chunk.start_char : chunk.end_char]
        assert len(tokenizer(chunk.text)["input_ids"]) <= 256
        assert chunk.token_count <= 192
        covered.update(range(chunk.start_char, chunk.end_char))
    assert covered == set(range(len(text)))


def test_tokenizer_limit_is_respected_without_silent_truncation():
    tokenizer = OffsetTokenizer()
    tokenizer.model_max_length = 10
    text = "word " * 30
    paragraph = Paragraph(
        paragraph_id="p:0",
        paper_id="p",
        section_index=0,
        section_name="Methods",
        paragraph_index=0,
        text=text,
        text_sha256=text_hash(text),
    )
    chunks = chunk_paragraph(paragraph, tokenizer, AppConfig())
    assert len(chunks) > 1
    assert all(len(tokenizer(c.text)["input_ids"]) <= 10 for c in chunks)
