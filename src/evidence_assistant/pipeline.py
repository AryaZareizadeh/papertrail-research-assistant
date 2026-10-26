"""File-oriented setup operations; no benchmark annotations enter the store."""

import json
from collections import Counter

from evidence_assistant.chunking import chunk_paragraph
from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, read_jsonl, text_hash, write_json, write_jsonl
from evidence_assistant.embedding import embedding_metadata
from evidence_assistant.schemas import Paper, Paragraph
from evidence_assistant.store import build_store


def build_chunks(config: AppConfig, tokenizer, *, all_papers: bool = False) -> dict:
    metadata = embedding_metadata(config)
    papers = [Paper(**p) for p in read_jsonl(config.corpus_dir / "papers.jsonl")]
    if not all_papers:
        manifest = json.loads((config.manifest_dir / "data_manifest.json").read_text("utf-8"))
        selected = {pid for ids in manifest["selected_paper_ids"].values() for pid in ids}
        papers = [p for p in papers if p.paper_id in selected]
    selected_ids = {p.paper_id for p in papers}
    paragraphs = [
        Paragraph(**p)
        for p in read_jsonl(config.corpus_dir / "paragraphs.jsonl")
        if p["paper_id"] in selected_ids
    ]
    chunks, rejected, overlong = [], [], 0
    for paragraph in paragraphs:
        try:
            windows = chunk_paragraph(paragraph, tokenizer, config)
        except ValueError as exc:
            rejected.append({"paragraph_id": paragraph.paragraph_id, "reason": str(exc)})
            continue
        overlong += len(windows) > 1
        chunks.extend(windows)
    write_jsonl(config.report_dir / "runs" / "chunk_rejections.jsonl", rejected)
    if rejected:
        raise ValueError(
            "Chunking rejected paragraphs; inspect reports/runs/chunk_rejections.jsonl"
        )
    build_store(papers, paragraphs, chunks, config.database_path)
    counts = Counter(p.text_sha256 for p in paragraphs)
    lengths = sorted(len(p.text) for p in paragraphs)
    manifest = {
        "chunking_version": config.chunking_version,
        "chunk_tokens": config.chunk_tokens,
        "chunk_overlap_tokens": config.chunk_overlap_tokens,
        "embedding_model": config.embedding_model,
        "embedding_revision": metadata["revision"],
        "effective_max_tokens": min(config.embedding_max_tokens, tokenizer.model_max_length),
        "database_hash": file_hash(config.database_path),
        "chunks_hash": text_hash("\n".join(c.model_dump_json() for c in chunks)),
        "papers": len(papers),
        "paragraphs": len(paragraphs),
        "chunks": len(chunks),
        "empty_paragraphs": sum(not p.text.strip() for p in paragraphs),
        "duplicate_text_occurrences": sum(n - 1 for n in counts.values()),
        "overlong_paragraphs_split": overlong,
        "paragraph_lengths": {
            "min": min(lengths, default=0),
            "max": max(lengths, default=0),
            "median": lengths[len(lengths) // 2] if lengths else 0,
        },
        "all_papers": all_papers,
    }
    write_json(config.artifact_dir / "chunking_manifest.json", manifest)
    return manifest
