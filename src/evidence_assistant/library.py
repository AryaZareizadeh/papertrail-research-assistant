"""Atomic per-paper user collection, separate from frozen benchmark assets."""

import re
import shutil
import time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock
from uuid import uuid4

from evidence_assistant.chunking import chunk_paragraph
from evidence_assistant.data import file_hash, write_json
from evidence_assistant.embedding import embedding_metadata
from evidence_assistant.paper_import import (
    ExtractedPaper,
    ImportProblem,
    extract_pdf_isolated,
    fetch_arxiv,
)
from evidence_assistant.retrieval import RetrievalIndex, build_index
from evidence_assistant.schemas import Paper, Record
from evidence_assistant.store import build_store, get_paragraph, list_papers


class ImportPreview(Record):
    preview_id: str
    paper_id: str
    title: str
    pages: int
    text_pages: int
    preview_text: str
    preview_truncated: bool
    origin: str
    warnings: list[str]


class ImportSaved(Record):
    paper: Paper
    already_exists: bool


class PaperLibrary:
    def __init__(self, config):
        self.config = config
        self.root = config.library_path
        self.lock = RLock()
        self._indices = {}

    def _bundle(self, paper_id):
        if not re.fullmatch(r"pdf-[a-f0-9]{64}", paper_id):
            return None
        path = self.root / paper_id
        return path if (path / "index_manifest.json").is_file() else None

    def papers(self):
        papers = []
        for path in sorted(self.root.glob("pdf-*")):
            if self._bundle(path.name):
                papers.extend(list_papers(path / "corpus.sqlite"))
        return papers

    def paragraphs(self, paper_id):
        from evidence_assistant.store import list_paragraphs

        bundle = self._bundle(paper_id)
        return list_paragraphs(bundle / "corpus.sqlite") if bundle else []

    def paragraph(self, paper_id, paragraph_id):
        bundle = self._bundle(paper_id)
        return get_paragraph(bundle / "corpus.sqlite", paper_id, paragraph_id) if bundle else None

    def database(self, paper_id):
        bundle = self._bundle(paper_id)
        return bundle / "corpus.sqlite" if bundle else None

    def preview(self, data: bytes, *, filename="paper.pdf", origin="PDF upload"):
        extracted = extract_pdf_isolated(data, filename=filename)
        extracted.origin = origin
        token = uuid4().hex
        with self.lock:
            pending = self.root / ".previews"
            pending.mkdir(parents=True, exist_ok=True)
            # Bound temporary disk use; old browser tabs can simply preview again.
            previous = sorted(pending.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
            for old in previous[9:]:
                if old.is_dir() and re.fullmatch(r"[a-f0-9]{32}", old.name):
                    shutil.rmtree(old)
            path = pending / token
            path.mkdir()
            try:
                (path / "source.pdf").write_bytes(data)
                write_json(path / "extracted.json", extracted)
            except OSError:
                shutil.rmtree(path, ignore_errors=True)
                raise ImportProblem("library_unavailable", 503) from None
        text = "\n\n".join(p.text for p in extracted.paragraphs)
        return ImportPreview(
            preview_id=token, paper_id=extracted.paper_id, title=extracted.title,
            pages=extracted.pages, text_pages=len(extracted.paragraphs),
            preview_text=text[:20_000], preview_truncated=len(text) > 20_000, origin=origin,
            warnings=[
                "Check the extracted text: PDF columns, equations and tables may lose formatting.",
                "Citations point to extracted page text; scanned pages without text are omitted.",
            ],
        )

    def preview_arxiv(self, value):
        with self.lock:
            data, origin = fetch_arxiv(value)
        return self.preview(data, origin=origin)

    def confirm(self, token, title, base_service):
        if not re.fullmatch(r"[a-f0-9]{32}", token):
            raise ImportProblem("preview_not_found", 404)
        path = self.root / ".previews" / token
        with self.lock:
            try:
                if time.time() - path.stat().st_mtime > 24 * 3600:
                    raise ImportProblem("preview_not_found", 404)
                extracted = ExtractedPaper.model_validate_json(
                    (path / "extracted.json").read_text("utf-8")
                )
                if file_hash(path / "source.pdf") != extracted.pdf_sha256:
                    raise ImportProblem("preview_not_found", 404)
            except (OSError, ValueError):
                raise ImportProblem("preview_not_found", 404) from None
            destination = self._bundle(extracted.paper_id)
            if destination:
                return ImportSaved(paper=list_papers(destination / "corpus.sqlite")[0],
                                   already_exists=True)
            title = title.strip()
            if not title or len(title) > 300:
                raise ImportProblem("invalid_title")
            paper = Paper(paper_id=extracted.paper_id, split="user", title=title,
                          abstract="", source_revision="pdf-text-v1:" + extracted.pdf_sha256)
            try:
                with TemporaryDirectory(prefix=".import-", dir=self.root) as temporary:
                    staging = Path(temporary) / "bundle"
                    staging.mkdir()
                    config = self.config.model_copy(update={"artifact_dir": staging})
                    encoder = base_service.index.encoder
                    if encoder is None:
                        raise ValueError("Import requires the prepared dense embedding encoder")
                    metadata = embedding_metadata(self.config)
                    write_json(staging / "embedding_model.json", metadata)
                    chunks = [chunk for paragraph in extracted.paragraphs
                              for chunk in chunk_paragraph(paragraph, encoder.tokenizer, config)]
                    build_store([paper], extracted.paragraphs, chunks, config.database_path)
                    write_json(staging / "chunking_manifest.json", {
                        "chunking_version": config.chunking_version,
                        "chunk_tokens": config.chunk_tokens,
                        "chunk_overlap_tokens": config.chunk_overlap_tokens,
                        "embedding_model": config.embedding_model,
                        "embedding_revision": metadata["revision"],
                        "effective_max_tokens": min(config.embedding_max_tokens,
                                                    encoder.tokenizer.model_max_length),
                        "database_hash": file_hash(config.database_path),
                    })
                    build_index(config.database_path, staging, config, encoder=encoder)
                    shutil.copyfile(path / "source.pdf", staging / "source.pdf")
                    write_json(staging / "source.json", {
                        "pdf_sha256": extracted.pdf_sha256, "origin": extracted.origin,
                        "pages": extracted.pages, "text_pages": len(extracted.paragraphs),
                        "extraction": "pypdf-page-text-v1",
                    })
                    # Load and verify before publication; partial bundles never reach the catalog.
                    RetrievalIndex.load(config, encoder=encoder)
                    staging.rename(self.root / extracted.paper_id)
            except (OSError, ValueError, ImportError):
                raise ImportProblem("library_unavailable", 503) from None
            return ImportSaved(paper=paper, already_exists=False)

    def service(self, paper_id, base_service):
        bundle = self._bundle(paper_id)
        if bundle is None:
            return base_service
        config = self.config.model_copy(update={"artifact_dir": bundle})
        with self.lock:
            if paper_id not in self._indices:
                self._indices[paper_id] = replace(
                    RetrievalIndex.load(config, encoder=base_service.index.encoder),
                    prefer_pdf_frontmatter=True,
                )
            index = self._indices[paper_id]
        return replace(base_service, config=config, index=index)
