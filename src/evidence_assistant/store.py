"""SQLite persistence boundary; a later PostgreSQL adapter can preserve these records."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from evidence_assistant.data import text_hash, write_json
from evidence_assistant.schemas import Chunk, Paper, Paragraph


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def build_store(
    papers: list[Paper], paragraphs: list[Paragraph], chunks: list[Chunk], db_path: Path
) -> None:
    source = {p.paragraph_id: p for p in paragraphs}
    paper_ids = {p.paper_id for p in papers}
    if len(source) != len(paragraphs) or len(paper_ids) != len(papers):
        raise ValueError("Duplicate source identifiers")
    for paragraph in paragraphs:
        if paragraph.paper_id not in paper_ids:
            raise ValueError("Paragraph refers to an unknown paper")
        if text_hash(paragraph.text) != paragraph.text_sha256:
            raise ValueError("Paragraph source hash mismatch")
    for chunk in chunks:
        paragraph = source.get(chunk.paragraph_id)
        if paragraph is None or chunk.paper_id != paragraph.paper_id:
            raise ValueError("Chunk refers to an unknown or mismatched paper/paragraph")
        if chunk.section_name != paragraph.section_name:
            raise ValueError("Chunk section differs from its source paragraph section")
        if paragraph.text[chunk.start_char : chunk.end_char] != chunk.text:
            raise ValueError("Chunk source span mismatch")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = db_path.with_suffix(".sqlite.tmp")
    temporary.unlink(missing_ok=True)
    try:
        with closing(sqlite3.connect(temporary)) as connection, connection:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.executescript("""
                CREATE TABLE papers (
                    paper_id TEXT PRIMARY KEY, split TEXT NOT NULL, record TEXT NOT NULL
                );
                CREATE TABLE paragraphs (
                    paragraph_id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL REFERENCES papers(paper_id), record TEXT NOT NULL
                );
                CREATE TABLE chunks (
                    chunk_id TEXT PRIMARY KEY,
                    paragraph_id TEXT NOT NULL REFERENCES paragraphs(paragraph_id),
                    paper_id TEXT NOT NULL REFERENCES papers(paper_id), record TEXT NOT NULL
                );
                CREATE INDEX paragraphs_paper ON paragraphs(paper_id);
                CREATE INDEX chunks_paper ON chunks(paper_id);
            """)
            connection.executemany(
                "INSERT INTO papers VALUES (?, ?, ?)",
                [(p.paper_id, p.split, p.model_dump_json()) for p in papers],
            )
            connection.executemany(
                "INSERT INTO paragraphs VALUES (?, ?, ?)",
                [(p.paragraph_id, p.paper_id, p.model_dump_json()) for p in paragraphs],
            )
            connection.executemany(
                "INSERT INTO chunks VALUES (?, ?, ?, ?)",
                [(c.chunk_id, c.paragraph_id, c.paper_id, c.model_dump_json()) for c in chunks],
            )
        temporary.replace(db_path)
    finally:
        temporary.unlink(missing_ok=True)


def _records(db_path: Path, query: str, params: tuple, record_type):
    with closing(connect_readonly(db_path)) as connection:
        return [
            record_type.model_validate_json(row["record"])
            for row in connection.execute(query, params)
        ]


def list_papers(db_path: Path) -> list[Paper]:
    return _records(db_path, "SELECT record FROM papers ORDER BY paper_id", (), Paper)


def get_paper(db_path: Path, paper_id: str) -> Paper | None:
    records = _records(db_path, "SELECT record FROM papers WHERE paper_id=?", (paper_id,), Paper)
    return records[0] if records else None


def list_paragraphs(db_path: Path, paper_id: str | None = None) -> list[Paragraph]:
    query = "SELECT record FROM paragraphs"
    params = () if paper_id is None else (paper_id,)
    if paper_id is not None:
        query += " WHERE paper_id=?"
    return _records(db_path, query + " ORDER BY paragraph_id", params, Paragraph)


def list_chunks(db_path: Path, paper_id: str | None = None) -> list[Chunk]:
    query = "SELECT record FROM chunks"
    params = () if paper_id is None else (paper_id,)
    if paper_id is not None:
        query += " WHERE paper_id=?"
    return _records(db_path, query + " ORDER BY chunk_id", params, Chunk)


def get_chunk(db_path: Path, chunk_id: str) -> Chunk | None:
    records = _records(db_path, "SELECT record FROM chunks WHERE chunk_id=?", (chunk_id,), Chunk)
    return records[0] if records else None


def get_paragraph(db_path: Path, paper_id: str, paragraph_id: str) -> Paragraph | None:
    records = _records(
        db_path,
        "SELECT record FROM paragraphs WHERE paper_id=? AND paragraph_id=?",
        (paper_id, paragraph_id),
        Paragraph,
    )
    return records[0] if records else None


def write_run(directory: Path, record: dict) -> None:
    """Keep mutable run records separate from the immutable corpus/index database."""
    write_json(directory / f"{record['request_id']}.json", record)
    with closing(sqlite3.connect(directory / "runs.sqlite")) as connection, connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS runs (
            request_id TEXT PRIMARY KEY, paper_id TEXT NOT NULL, status TEXT NOT NULL,
            latency_ms REAL NOT NULL, record TEXT NOT NULL
        )""")
        connection.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?)",
            (
                record["request_id"],
                record["paper_id"],
                record["status"],
                record["latency_ms"],
                json.dumps(record, ensure_ascii=False),
            ),
        )
