"""Paper-scoped BM25, cosine, and reciprocal-rank-fusion baselines."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
from rank_bm25 import BM25Okapi

from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, text_hash, write_json
from evidence_assistant.document_questions import is_authorship_question
from evidence_assistant.embedding import embedding_metadata, load_encoder
from evidence_assistant.schemas import Chunk, IndexManifest, RetrievedChunk
from evidence_assistant.store import list_chunks, list_papers


def tokenize(text: str) -> list[str]:
    """Case-fold and extract Unicode word/number tokens, excluding underscores."""
    return re.findall(r"[^\W_]+", text.casefold())


def _normalize(vectors):
    vectors = np.asarray(vectors, dtype=np.float32)
    if vectors.ndim != 2 or not np.isfinite(vectors).all():
        raise ValueError("Embedding vectors must be a finite matrix")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Zero embedding vectors are not supported")
    return vectors / norms


def _chunk_policy(config: AppConfig) -> dict:
    return {
        "chunking_version": config.chunking_version,
        "chunk_tokens": config.chunk_tokens,
        "chunk_overlap_tokens": config.chunk_overlap_tokens,
    }


def _validate_chunking(config: AppConfig, db_path: Path) -> dict:
    policy = json.loads((config.artifact_dir / "chunking_manifest.json").read_text("utf-8"))
    metadata = embedding_metadata(config)
    if any(policy.get(k) != v for k, v in _chunk_policy(config).items()):
        raise ValueError("Index chunk settings changed; rebuild chunks before indexing")
    if policy.get("embedding_model") != metadata["model"] or (
        policy.get("embedding_revision") != metadata["revision"]
    ):
        raise ValueError("Chunk tokenizer model/revision differs; rebuild chunks")
    if policy.get("database_hash") != file_hash(db_path):
        raise ValueError("Chunk corpus hash mismatch")
    if policy.get("effective_max_tokens") != min(
        config.embedding_max_tokens,
        metadata.get("effective_max_tokens", config.embedding_max_tokens),
    ):
        raise ValueError("Chunk tokenizer input limit changed; rebuild chunks")
    return policy


def build_index(
    db_path: Path, output_dir: Path, config: AppConfig, *, encoder=None
) -> IndexManifest:
    started = perf_counter()
    metadata = embedding_metadata(config)
    chunking_path = output_dir / "chunking_manifest.json"
    policy = _validate_chunking(config, db_path)
    chunks = list_chunks(db_path)
    if not chunks:
        raise ValueError("No chunks to index")
    loaded_here = encoder is None
    load_started = perf_counter()
    encoder = load_encoder(config) if loaded_here else encoder
    model_load_ms = (perf_counter() - load_started) * 1000 if loaded_here else 0.0
    actual_limit = min(
        encoder.max_seq_length, encoder.tokenizer.model_max_length, config.embedding_max_tokens
    )
    for chunk in chunks:
        actual_tokens = len(encoder.tokenizer(chunk.text, truncation=False)["input_ids"])
        if actual_tokens > actual_limit:
            raise ValueError("Chunk exceeds the encoder's actual input limit; rebuild chunks")
    encode_started = perf_counter()
    vectors = _normalize(
        encoder.encode([c.text for c in chunks], normalize_embeddings=True, show_progress_bar=False)
    )
    embedding_encode_ms = (perf_counter() - encode_started) * 1000
    if len(vectors) != len(chunks):
        raise ValueError("Embedding row count does not match chunks")
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary = output_dir / "embeddings.tmp.npy"
    np.save(temporary, vectors, allow_pickle=False)
    vector_hash = file_hash(temporary)
    vector_path = output_dir / f"embeddings-{vector_hash}.npy"
    temporary.replace(vector_path)
    corpus_hash = file_hash(db_path)
    manifest = IndexManifest(
        vector_file=vector_path.name,
        corpus_hash=corpus_hash,
        chunking_hash=file_hash(chunking_path),
        embedding_model=config.embedding_model,
        embedding_revision=metadata["revision"],
        tokenizer_settings={
            **_chunk_policy(config),
            "embedding_max_tokens": config.embedding_max_tokens,
            "effective_max_tokens": policy["effective_max_tokens"],
        },
        vector_dimension=vectors.shape[1],
        ordered_chunk_ids=[c.chunk_id for c in chunks],
        artifact_hashes={vector_path.name: vector_hash},
        index_version=text_hash(corpus_hash + file_hash(vector_path) + metadata["revision"]),
    )
    write_json(output_dir / "index_manifest.json", manifest)
    elapsed_ms = (perf_counter() - started) * 1000
    write_json(
        output_dir / "index_build.json",
        {
            "elapsed_ms": elapsed_ms,
            "includes_model_load": loaded_here,
            "model_load_ms": model_load_ms,
            "index_build_ms": elapsed_ms - model_load_ms,
            "embedding_encode_ms": embedding_encode_ms,
        },
    )
    return manifest


@dataclass
class RetrievalIndex:
    chunks: list[Chunk]
    paper_ids: set[str]
    vectors: np.ndarray | None
    encoder: object | None
    config: AppConfig
    index_version: str
    prefer_pdf_frontmatter: bool = False

    @classmethod
    def load(cls, config: AppConfig, *, encoder=None, method: str | None = None):
        _validate_chunking(config, config.database_path)
        chunks = list_chunks(config.database_path)
        papers = {p.paper_id for p in list_papers(config.database_path)}
        if method == "bm25":
            return cls(chunks, papers, None, None, config, file_hash(config.database_path))
        manifest = IndexManifest.model_validate_json(
            (config.artifact_dir / "index_manifest.json").read_text("utf-8")
        )
        metadata = embedding_metadata(config)
        if manifest.embedding_model != config.embedding_model or (
            manifest.embedding_revision != metadata["revision"]
        ):
            raise ValueError("Embedding model/revision mismatch")
        if manifest.corpus_hash != file_hash(config.database_path):
            raise ValueError("Corpus hash mismatch; rebuild the index")
        if manifest.chunking_hash != file_hash(config.artifact_dir / "chunking_manifest.json"):
            raise ValueError("Chunking manifest hash mismatch")
        for name, value in {
            **_chunk_policy(config),
            "embedding_max_tokens": config.embedding_max_tokens,
        }.items():
            if manifest.tokenizer_settings.get(name) != value:
                raise ValueError("Index chunk/tokenizer policy differs from configuration")
        if manifest.ordered_chunk_ids != [c.chunk_id for c in chunks]:
            raise ValueError("Index chunk order mismatch")
        if Path(manifest.vector_file).name != manifest.vector_file:
            raise ValueError("Index vector file must be a local artifact filename")
        path = config.artifact_dir / manifest.vector_file
        if file_hash(path) != manifest.artifact_hashes[manifest.vector_file]:
            raise ValueError("Embedding artifact hash mismatch")
        vectors = np.load(path, allow_pickle=False)
        if vectors.shape != (len(chunks), manifest.vector_dimension):
            raise ValueError("Embedding row count or dimension mismatch")
        if not np.isfinite(vectors).all() or not np.allclose(
            np.linalg.norm(vectors, axis=1), 1, atol=1e-4
        ):
            raise ValueError("Embedding vectors must be finite and normalized")
        return cls(
            chunks,
            papers,
            vectors,
            load_encoder(config) if encoder is None else encoder,
            config,
            manifest.index_version,
        )


def retrieve(
    question: str, paper_id: str, method: str, top_k: int, index: RetrievalIndex
) -> list[RetrievedChunk]:
    if method not in {"bm25", "dense", "hybrid"} or top_k < 1:
        raise ValueError("Invalid retrieval method or top_k")
    if paper_id not in index.paper_ids:
        raise KeyError(f"Unknown paper: {paper_id}")
    rows = [i for i, chunk in enumerate(index.chunks) if chunk.paper_id == paper_id]
    if not rows:
        return []
    chunks = [index.chunks[i] for i in rows]

    def rank(scores):
        return sorted(range(len(chunks)), key=lambda i: (-float(scores[i]), chunks[i].chunk_id))

    rankings, scores = {}, None
    if method in {"bm25", "hybrid"}:
        tokens = [tokenize(c.text) for c in chunks]
        scores = (
            BM25Okapi(tokens).get_scores(tokenize(question))
            if any(tokens)
            else np.zeros(len(chunks))
        )
        rankings["bm25"] = rank(scores)
    if method in {"dense", "hybrid"}:
        if index.encoder is None or index.vectors is None:
            raise ValueError("Dense retrieval requires an embedding index")
        query = _normalize(index.encoder.encode([question], normalize_embeddings=True))[0]
        if len(query) != index.vectors.shape[1]:
            raise ValueError("Query embedding dimension mismatch")
        scores = index.vectors[rows] @ query
        rankings["dense"] = rank(scores)
    if method == "hybrid":
        scores = np.zeros(len(chunks))
        for ranking in rankings.values():
            for position, i in enumerate(ranking[: index.config.candidate_k], start=1):
                scores[i] += 1 / (index.config.rrf_k + position)
        ordered = [i for i in rank(scores) if scores[i] > 0]
    else:
        ordered = rankings[method]
    if index.prefer_pdf_frontmatter and is_authorship_question(question):
        front = sorted(
            (i for i, chunk in enumerate(chunks) if chunk.section_name == "Page 1"),
            key=lambda i: chunks[i].start_char,
        )[:2]
        ordered = front + [i for i in ordered if i not in front]
    return [
        RetrievedChunk(chunk=chunks[i], rank=position, score=float(scores[i]), method=method)
        for position, i in enumerate(ordered[:top_k], start=1)
    ]
