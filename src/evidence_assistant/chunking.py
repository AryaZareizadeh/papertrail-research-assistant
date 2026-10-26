"""Token-bounded windows whose text is always sliced from the original paragraph."""

from evidence_assistant.config import AppConfig
from evidence_assistant.schemas import Chunk, Paragraph


def chunk_paragraph(paragraph: Paragraph, tokenizer, config: AppConfig) -> list[Chunk]:
    if not paragraph.text.strip():
        return []
    encoded = tokenizer(
        paragraph.text, add_special_tokens=False, return_offsets_mapping=True, truncation=False
    )
    offsets = encoded["offset_mapping"]
    if not offsets:
        raise ValueError(f"Tokenizer lost non-empty paragraph {paragraph.paragraph_id}")
    limit = min(config.embedding_max_tokens, tokenizer.model_max_length)
    empty_specials = len(tokenizer("", add_special_tokens=True)["input_ids"])
    window = min(config.chunk_tokens, limit - empty_specials)
    if window < 1:
        raise ValueError("Embedding tokenizer has no room for content tokens")
    overlap = min(config.chunk_overlap_tokens, window - 1)
    chunks, start = [], 0
    while start < len(offsets):
        stop = min(start + window, len(offsets))
        char_start = 0 if start == 0 else offsets[start][0]
        char_end = len(paragraph.text) if stop == len(offsets) else offsets[stop][0]
        text = paragraph.text[char_start:char_end]
        # Tokenization at a substring boundary can differ; never silently truncate.
        while len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"]) > limit:
            stop -= 1
            if stop <= start:
                raise ValueError("A source token cannot fit within the embedding input limit")
            char_end = offsets[stop][0]
            text = paragraph.text[char_start:char_end]
        token_count = len(tokenizer(text, add_special_tokens=False)["input_ids"])
        chunks.append(
            Chunk(
                chunk_id=f"{paragraph.paragraph_id}:c{len(chunks):04d}",
                paragraph_id=paragraph.paragraph_id,
                paper_id=paragraph.paper_id,
                section_name=paragraph.section_name,
                start_char=char_start,
                end_char=char_end,
                text=text,
                token_count=token_count,
                chunking_version=config.chunking_version,
            )
        )
        if stop == len(offsets):
            break
        start = max(start + 1, stop - overlap)
    return chunks
