"""Portable bundle checks use tiny synthetic model files, no downloads/inference."""

import json

import pytest

from evidence_assistant.config import AppConfig
from evidence_assistant.data import file_hash
from evidence_assistant.runtime_export import export_runtime


def test_export_only_runtime_assets_and_preserves_bytes(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    encoder = tmp_path / "encoder"
    tokenizer = tmp_path / "generator"
    encoder.mkdir()
    tokenizer.mkdir()
    (encoder / "model.safetensors").write_bytes(b"synthetic weights")
    (encoder / "config.json").write_text("{}", encoding="utf-8")
    (tokenizer / "tokenizer.json").write_text("{}", encoding="utf-8")
    for name in [
        "corpus.sqlite",
        "embeddings.npy",
        "chunking_manifest.json",
        "generation_token_calibration.json",
    ]:
        (artifacts / name).write_bytes(b"unchanged")
    (artifacts / "embedding_model.json").write_text(
        json.dumps({"snapshot": str(encoder), "revision": "pinned"})
    )
    (artifacts / "generation_tokenizer.json").write_text(
        json.dumps(
            {
                "snapshot": str(tokenizer),
                "file_hashes": {"tokenizer.json": file_hash(tokenizer / "tokenizer.json")},
            }
        )
    )
    (artifacts / "index_manifest.json").write_text(json.dumps({"vector_file": "embeddings.npy"}))
    (artifacts / "PRIVATE_BENCHMARK.json").write_text("GOLD_SECRET")
    config = AppConfig(artifact_dir=artifacts)
    output = tmp_path / "bundle"
    result = export_runtime(config, output)
    assert not (output / "PRIVATE_BENCHMARK.json").exists()
    assert (output / "corpus.sqlite").read_bytes() == b"unchanged"
    assert (output / "models/embedding/model.safetensors").read_bytes() == b"synthetic weights"
    assert (
        json.loads((output / "embedding_model.json").read_text())["snapshot"]
        == "/artifacts/models/embedding"
    )
    assert (
        json.loads((output / "generation_tokenizer.json").read_text())["snapshot"]
        == "/artifacts/models/generation"
    )
    assert (output / "generation_token_calibration.json").read_bytes() == b"unchanged"
    for name, expected in result["file_hashes"].items():
        assert file_hash(output / name) == expected
    with pytest.raises(ValueError, match="exists"):
        export_runtime(config, output)


def test_export_rejects_parent_traversal_in_artifact_names(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "index_manifest.json").write_text(json.dumps({"vector_file": "../private.npy"}))
    with pytest.raises(ValueError, match="filename"):
        export_runtime(AppConfig(artifact_dir=artifacts), tmp_path / "bundle")


@pytest.mark.parametrize("snapshot", ["encoder", "generator"])
def test_export_rejects_destination_inside_model_snapshot(tmp_path, monkeypatch, snapshot):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    for name in ("encoder", "generator"):
        (tmp_path / name).mkdir()
    (tmp_path / "encoder/model.safetensors").write_bytes(b"weights")
    for name in (
        "corpus.sqlite",
        "chunking_manifest.json",
        "embeddings.npy",
        "generation_token_calibration.json",
    ):
        (artifacts / name).write_bytes(b"unchanged")
    (artifacts / "index_manifest.json").write_text(json.dumps({"vector_file": "embeddings.npy"}))
    (artifacts / "embedding_model.json").write_text(
        json.dumps({"snapshot": str(tmp_path / "encoder")})
    )
    (artifacts / "generation_tokenizer.json").write_text(
        json.dumps({"snapshot": str(tmp_path / "generator"), "file_hashes": {}})
    )

    # Bound the buggy path before recursive copying can consume disk space.
    def stop_copy(*args, **kwargs):
        raise RuntimeError("Copy began before overlap was rejected")

    monkeypatch.setattr("evidence_assistant.runtime_export.shutil.copyfile", stop_copy)
    output = tmp_path / snapshot / "nested" / "bundle"
    with pytest.raises(ValueError, match="separate"):
        export_runtime(AppConfig(artifact_dir=artifacts), output)
    assert not output.parent.exists()
