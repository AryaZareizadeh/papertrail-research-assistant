import io
import json
import tarfile

import httpx
import pytest

from evidence_assistant.data import download_qasper, normalize_release, read_jsonl, select_papers


def test_normalizer_separates_runtime_and_gold(qasper_release, tmp_path):
    corpus, gold = tmp_path / "corpus", tmp_path / "gold"
    manifest = normalize_release(qasper_release, corpus, gold)
    assert "GOLD_SECRET" not in "".join(p.read_text() for p in corpus.glob("*.jsonl"))
    questions = read_jsonl(gold / "questions.jsonl")
    assert questions[0]["references"][0]["answer_text"] == "GOLD_SECRET_DO_NOT_INDEX"
    assert len(questions[0]["references"]) == 2
    assert questions[0]["annotation_disagreement"] is True
    assert manifest.observed_split_counts["train"] == {
        "papers": 1,
        "questions": 1,
        "annotations": 2,
    }
    paragraphs = read_jsonl(corpus / "paragraphs.jsonl")
    train = [p for p in paragraphs if p["paper_id"] == "paper-train"]
    assert train[0]["paragraph_id"] == "paper-train:abstract:p0000"
    assert train[1]["paragraph_id"] == "paper-train:s0000:p0000"
    assert train[2]["paragraph_id"] == "paper-train:s0000:p0001"
    assert train[1]["text"] == train[2]["text"]


def test_split_overlap_fails_before_writing_exports(qasper_release, tmp_path):
    path = qasper_release / "qasper-test-v0.3.json"
    data = json.loads(path.read_text())
    path.write_text(json.dumps({"paper-train": next(iter(data.values()))}))
    with pytest.raises(ValueError, match="overlap"):
        normalize_release(qasper_release, tmp_path / "corpus", tmp_path / "gold")
    assert not (tmp_path / "corpus").exists()


def test_selection_is_order_independent_and_retains_all_selected_questions():
    expected = select_papers(["a", "b", "c", "d"], "validation", 2, 42)
    assert select_papers(["d", "c", "b", "a"], "validation", 2, 42) == expected
    assert len(set(expected)) == 2
    with pytest.raises(ValueError):
        select_papers(["a"], "train", -1, 42)


def test_overlapping_exports_are_rejected(qasper_release, tmp_path):
    with pytest.raises(ValueError, match="overlap"):
        normalize_release(qasper_release, tmp_path / "data", tmp_path / "data" / "gold")


def test_download_extracts_only_allowlisted_regular_files(tmp_path):
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name in [
            "../../escape.txt",
            "qasper-train-v0.3.json",
            "qasper-dev-v0.3.json",
            "qasper-test-v0.3.json",
        ]:
            info = tarfile.TarInfo(name)
            info.size = 2
            archive.addfile(info, io.BytesIO(b"{}"))
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, content=payload.getvalue())
        )
    )
    manifest = download_qasper(tmp_path / "raw", client=client)
    assert not (tmp_path / "escape.txt").exists()
    assert (tmp_path / "raw" / "qasper-train-v0.3.json").read_text() == "{}"
    assert len(manifest.file_hashes) == 5


def test_bad_download_leaves_no_completed_archive(tmp_path):
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503)))
    with pytest.raises(httpx.HTTPStatusError):
        download_qasper(tmp_path / "raw", client=client)
    assert not list((tmp_path / "raw").glob("*.tgz"))


def test_normalization_keeps_archive_provenance(qasper_release, tmp_path):
    (qasper_release / "download_manifest.json").write_text(
        json.dumps({"file_hashes": {"qasper-train-dev-v0.3.tgz": "archive-checksum"}})
    )
    manifest = normalize_release(qasper_release, tmp_path / "corpus", tmp_path / "gold")
    assert manifest.file_hashes["qasper-train-dev-v0.3.tgz"] == "archive-checksum"


def test_invalid_archive_does_not_overwrite_existing_source(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    previous = raw / "qasper-train-v0.3.json"
    previous.write_text('{"previous": "good"}')
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        info = tarfile.TarInfo("qasper-train-v0.3.json")
        info.size = 2
        archive.addfile(info, io.BytesIO(b"{}"))
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, content=payload.getvalue())
        )
    )
    with pytest.raises(ValueError, match="missing"):
        download_qasper(raw, client=client)
    assert previous.read_text() == '{"previous": "good"}'
    assert not list(raw.glob("*.tgz"))
