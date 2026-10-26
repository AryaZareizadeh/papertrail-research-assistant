import json

from evidence_assistant.config import AppConfig
from evidence_assistant.data import normalize_release, read_jsonl, save_pilot_manifests
from evidence_assistant.pipeline import build_chunks
from evidence_assistant.store import list_papers
from tests.helpers import OffsetTokenizer


def test_pilot_build_uses_only_selected_papers_and_records_stats(qasper_release, tmp_path):
    corpus, gold = tmp_path / "corpus", tmp_path / "gold"
    manifest = normalize_release(qasper_release, corpus, gold)
    config = AppConfig(
        raw_dir=qasper_release,
        corpus_dir=corpus,
        evaluation_dir=gold,
        manifest_dir=tmp_path / "manifests",
        artifact_dir=tmp_path / "artifacts",
        report_dir=tmp_path / "reports",
    )
    save_pilot_manifests(manifest, read_jsonl(corpus / "papers.jsonl"), config.manifest_dir, 42)
    path = config.manifest_dir / "data_manifest.json"
    data = json.loads(path.read_text())
    data["selected_paper_ids"] = {"train": ["paper-train"]}
    path.write_text(json.dumps(data))
    config.artifact_dir.mkdir(parents=True)
    (config.artifact_dir / "embedding_model.json").write_text(
        json.dumps(
            {
                "model": config.embedding_model,
                "revision": "synthetic-test-revision",
                "snapshot": ".",
                "effective_max_tokens": 256,
            }
        )
    )
    summary = build_chunks(config, OffsetTokenizer())
    assert [p.paper_id for p in list_papers(config.database_path)] == ["paper-train"]
    assert summary["duplicate_text_occurrences"] == 1
    assert summary["paragraphs"] == 3
    assert summary["chunks"] == 3
    assert len(summary["database_hash"]) == 64
