import json

import pytest

from evidence_assistant.chunking import chunk_paragraph
from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash, text_hash
from evidence_assistant.retrieval import RetrievalIndex, build_index, retrieve
from evidence_assistant.schemas import Paper, Paragraph
from evidence_assistant.store import build_store
from tests.helpers import OffsetTokenizer


class TinyEncoder:
    """Deterministic vectors exercise ranking mechanics, never semantic model quality."""

    max_seq_length = 256
    tokenizer = OffsetTokenizer()

    def encode(self, texts, **kwargs):
        import numpy as np

        return np.array(
            [[float("dataset" in t.lower()), float("metric" in t.lower()), 0.1] for t in texts],
            dtype="float32",
        )


@pytest.fixture
def retrieval_setup(tmp_path):
    config = AppConfig(artifact_dir=tmp_path / "artifacts")
    papers = [
        Paper(paper_id=pid, split="train", title=pid, abstract="", source_revision="test")
        for pid in ["selected", "other", "empty"]
    ]
    paragraphs = []
    for pid, texts in [
        ("selected", ["Dataset Alpha", "metric accuracy", "training hardware"]),
        ("other", ["Dataset Alpha dataset dataset"]),
        ("empty", []),
    ]:
        for i, text in enumerate(texts):
            paragraphs.append(
                Paragraph(
                    paragraph_id=f"{pid}:s0000:p{i:04d}",
                    paper_id=pid,
                    section_index=0,
                    section_name="Methods",
                    paragraph_index=i,
                    text=text,
                    text_sha256=text_hash(text),
                )
            )
    chunks = [c for p in paragraphs for c in chunk_paragraph(p, OffsetTokenizer(), config)]
    build_store(papers, paragraphs, chunks, config.database_path)
    config.artifact_dir.joinpath("embedding_model.json").write_text(
        json.dumps(
            {
                "model": config.embedding_model,
                "revision": "synthetic-test-revision",
                "snapshot": ".",
            }
        )
    )
    config.artifact_dir.joinpath("chunking_manifest.json").write_text(
        json.dumps(
            {
                "chunking_version": config.chunking_version,
                "chunk_tokens": config.chunk_tokens,
                "chunk_overlap_tokens": config.chunk_overlap_tokens,
                "embedding_model": config.embedding_model,
                "embedding_revision": "synthetic-test-revision",
                "effective_max_tokens": 256,
                "database_hash": file_hash(config.database_path),
            }
        )
    )
    build_index(config.database_path, config.artifact_dir, config, encoder=TinyEncoder())
    return config


@pytest.mark.parametrize("method", ["bm25", "dense", "hybrid"])
def test_selected_paper_is_filtered_before_ranking(retrieval_setup, method):
    index = RetrievalIndex.load(retrieval_setup, encoder=TinyEncoder())
    results = retrieve("dataset", "selected", method, 5, index)
    assert results
    assert all(r.chunk.paper_id == "selected" for r in results)
    assert results[0].chunk.text == "Dataset Alpha"
    assert retrieve("dataset", "empty", method, 5, index) == []
    with pytest.raises(KeyError):
        retrieve("dataset", "missing", method, 5, index)


def test_stale_embeddings_fail_hash_validation(retrieval_setup):
    manifest = json.loads((retrieval_setup.artifact_dir / "index_manifest.json").read_text())
    path = retrieval_setup.artifact_dir / manifest.get("vector_file", "embeddings.npy")
    path.write_bytes(path.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="hash"):
        RetrievalIndex.load(retrieval_setup, encoder=TinyEncoder())


def test_changed_chunk_policy_requires_reindex(retrieval_setup):
    changed = retrieval_setup.model_copy(update={"chunk_tokens": 100})
    with pytest.raises(ValueError, match="chunk"):
        RetrievalIndex.load(changed, encoder=TinyEncoder())


def test_wrong_vector_order_is_rejected(retrieval_setup):
    path = retrieval_setup.artifact_dir / "index_manifest.json"
    value = json.loads(path.read_text())
    value["ordered_chunk_ids"].reverse()
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="order"):
        RetrievalIndex.load(retrieval_setup, encoder=TinyEncoder())


def test_bm25_rejects_changed_chunk_settings(retrieval_setup):
    changed = retrieval_setup.model_copy(update={"chunk_tokens": 100})
    with pytest.raises(ValueError, match="chunk"):
        RetrievalIndex.load(changed, method="bm25")


def test_changed_model_revision_requires_rechunking(retrieval_setup):
    path = retrieval_setup.artifact_dir / "embedding_model.json"
    metadata = json.loads(path.read_text())
    metadata["revision"] = "different-revision"
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="revision"):
        build_index(
            retrieval_setup.database_path,
            retrieval_setup.artifact_dir,
            retrieval_setup,
            encoder=TinyEncoder(),
        )


def test_encoder_limit_is_checked_before_encoding(retrieval_setup):
    encoder = TinyEncoder()
    encoder.max_seq_length = 3
    with pytest.raises(ValueError, match="limit"):
        build_index(
            retrieval_setup.database_path,
            retrieval_setup.artifact_dir,
            retrieval_setup,
            encoder=encoder,
        )


def test_failed_manifest_publication_preserves_previous_index(retrieval_setup, monkeypatch):
    import numpy as np

    import evidence_assistant.retrieval as module

    class DifferentEncoder(TinyEncoder):
        def encode(self, texts, **kwargs):
            return np.array([[0.0, 1.0, 0.0] for _ in texts], dtype="float32")

    original = module.write_json

    def fail_manifest(path, value):
        if path.name == "index_manifest.json":
            raise OSError("simulated publication failure")
        return original(path, value)

    monkeypatch.setattr(module, "write_json", fail_manifest)
    with pytest.raises(OSError):
        build_index(
            retrieval_setup.database_path,
            retrieval_setup.artifact_dir,
            retrieval_setup,
            encoder=DifferentEncoder(),
        )
    index = RetrievalIndex.load(retrieval_setup, encoder=TinyEncoder())
    assert retrieve("dataset", "selected", "dense", 1, index)[0].chunk.text == "Dataset Alpha"
