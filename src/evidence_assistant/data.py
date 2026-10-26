"""Explicit QASPER archive adapter with isolated runtime and evaluation exports."""

import hashlib
import json
import tarfile
from collections.abc import Iterable
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx

from evidence_assistant.schemas import AnswerReference, DataManifest, GoldQuestion, Paper, Paragraph

RELEASES = {
    "train": "qasper-train-v0.3.json",
    "validation": "qasper-dev-v0.3.json",
    "test": "qasper-test-v0.3.json",
}
ARCHIVES = {
    "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz": {
        RELEASES["train"],
        RELEASES["validation"],
    },
    "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz": {
        RELEASES["test"]
    },
}


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value = value.model_dump(mode="json") if hasattr(value, "model_dump") else value
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def write_jsonl(path: Path, records: Iterable) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for record in records:
            value = record.model_dump(mode="json") if hasattr(record, "model_dump") else record
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")
    temporary.replace(path)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def download_qasper(destination: Path, *, client: httpx.Client | None = None) -> DataManifest:
    destination.mkdir(parents=True, exist_ok=True)
    manifest = DataManifest(source_urls=list(ARCHIVES))
    context = nullcontext(client) if client else httpx.Client(timeout=120, follow_redirects=True)
    with context as connection:
        for url, expected in ARCHIVES.items():
            archive_path = destination / url.rsplit("/", 1)[1]
            with TemporaryDirectory(prefix=".qasper-staging-", dir=destination) as temporary_dir:
                staging = Path(temporary_dir)
                downloaded = not archive_path.exists()
                candidate = staging / archive_path.name if downloaded else archive_path
                if downloaded:
                    with connection.stream("GET", url) as response:
                        response.raise_for_status()
                        with candidate.open("wb") as handle:
                            for block in response.iter_bytes():
                                handle.write(block)
                found = set()
                with tarfile.open(candidate, "r:gz") as archive:
                    for member in archive.getmembers():
                        name = member.name.rsplit("/", 1)[-1]
                        if name not in expected:
                            continue
                        if not member.isfile() or name in found:
                            raise ValueError(f"Invalid or duplicate archive member: {member.name}")
                        found.add(name)
                        source = archive.extractfile(member)
                        if source is None:
                            raise ValueError(f"Unreadable archive member: {member.name}")
                        target = staging / name
                        with source, target.open("wb") as handle:
                            while block := source.read(1024 * 1024):
                                handle.write(block)
                        if not isinstance(json.loads(target.read_text("utf-8")), dict):
                            raise ValueError(f"Expected paper mapping in {name}")
                if found != expected:
                    raise ValueError(f"Archive missing expected files: {sorted(expected - found)}")
                # Only validated, complete archive contents can replace previous source files.
                for name in sorted(found):
                    (staging / name).replace(destination / name)
                    manifest.file_hashes[name] = file_hash(destination / name)
                if downloaded:
                    candidate.replace(archive_path)
                manifest.file_hashes[archive_path.name] = file_hash(archive_path)
    write_json(destination / "download_manifest.json", manifest)
    return manifest


def select_papers(paper_ids: list[str], split: str, limit: int, seed: int) -> list[str]:
    if limit < 0:
        raise ValueError("paper limit must not be negative")
    return sorted(
        set(paper_ids), key=lambda paper_id: (text_hash(f"{seed}{split}{paper_id}"), paper_id)
    )[:limit]


def _reference(question_id: str, index: int, record: dict) -> AnswerReference:
    answer = record["answer"]
    if answer["unanswerable"]:
        kind, text = "unanswerable", "Unanswerable"
    elif answer.get("yes_no") is not None:
        kind, text = "boolean", "Yes" if answer["yes_no"] else "No"
    elif answer.get("extractive_spans"):
        kind, text = "extractive", ", ".join(answer["extractive_spans"])
    else:
        kind, text = "abstractive", answer.get("free_form_answer", "")
    return AnswerReference(
        annotation_id=str(record.get("annotation_id", f"{question_id}:a{index:04d}")),
        answer_type=kind,
        answer_text=text,
        unanswerable=answer["unanswerable"],
        evidence=answer.get("evidence", []),
        highlighted_evidence=answer.get("highlighted_evidence", []),
        raw_answer=answer,
    )


def normalize_release(raw_dir: Path, corpus_dir: Path, evaluation_dir: Path) -> DataManifest:
    paths = [p.resolve() for p in (raw_dir, corpus_dir, evaluation_dir)]
    for index, a in enumerate(paths):
        for b in paths[index + 1 :]:
            if a.is_relative_to(b) or b.is_relative_to(a):
                raise ValueError("Raw, corpus, and evaluation directories must not overlap")
    releases = {}
    seen = set()
    manifest = DataManifest(source_urls=list(ARCHIVES))
    download_manifest = raw_dir / "download_manifest.json"
    if download_manifest.is_file():
        downloaded = json.loads(download_manifest.read_text(encoding="utf-8"))
        manifest.file_hashes.update(downloaded.get("file_hashes", {}))
    for split, name in RELEASES.items():
        path = raw_dir / name
        releases[split] = json.loads(path.read_text(encoding="utf-8"))
        ids = set(releases[split])
        if seen & ids:
            raise ValueError(f"Paper split overlap: {sorted(seen & ids)}")
        seen.update(ids)
        manifest.file_hashes[name] = file_hash(path)
    papers, paragraphs, questions = [], [], []
    question_ids = set()
    for split, release in releases.items():
        n_questions = n_annotations = 0
        for paper_id, raw in release.items():
            papers.append(
                Paper(
                    paper_id=paper_id,
                    split=split,
                    title=raw["title"],
                    abstract=raw["abstract"],
                    source_revision="qasper-v0.3",
                )
            )
            source_paragraphs = [
                (si, section.get("section_name") or "Untitled", pi, text)
                for si, section in enumerate(raw["full_text"])
                for pi, text in enumerate(section["paragraphs"])
            ]
            if raw["abstract"] and raw["abstract"] not in [p[3] for p in source_paragraphs]:
                source_paragraphs.insert(0, (-1, "Abstract", 0, raw["abstract"]))
            for si, section_name, pi, text in source_paragraphs:
                position = "abstract:p0000" if si == -1 else f"s{si:04d}:p{pi:04d}"
                paragraphs.append(
                    Paragraph(
                        paragraph_id=f"{paper_id}:{position}",
                        paper_id=paper_id,
                        section_index=si,
                        section_name=section_name,
                        paragraph_index=pi,
                        text=text,
                        text_sha256=text_hash(text),
                    )
                )
            for question in raw["qas"]:
                qid = question["question_id"]
                if qid in question_ids:
                    raise ValueError(f"Duplicate question ID: {qid}")
                question_ids.add(qid)
                refs = [_reference(qid, i, ref) for i, ref in enumerate(question["answers"])]
                n_questions += 1
                n_annotations += len(refs)
                questions.append(
                    GoldQuestion(
                        question_id=qid,
                        paper_id=paper_id,
                        question=question["question"],
                        references=refs,
                        annotation_disagreement=len({r.unanswerable for r in refs}) > 1,
                        uses_float_evidence=any(
                            e.startswith("FLOAT SELECTED") for ref in refs for e in ref.evidence
                        ),
                    )
                )
        manifest.observed_split_counts[split] = {
            "papers": len(release),
            "questions": n_questions,
            "annotations": n_annotations,
        }
    write_jsonl(corpus_dir / "papers.jsonl", papers)
    write_jsonl(corpus_dir / "paragraphs.jsonl", paragraphs)
    write_jsonl(evaluation_dir / "questions.jsonl", questions)
    return manifest


def save_pilot_manifests(
    manifest: DataManifest, papers: list[dict], output: Path, seed: int
) -> None:
    for split, limit, name in (
        ("train", 5, "debug"),
        ("validation", 30, "validation_pilot"),
        ("test", 50, "test_pilot"),
    ):
        ids = [p["paper_id"] for p in papers if p["split"] == split]
        selected = select_papers(ids, split, limit, seed)
        manifest.selected_paper_ids[split] = selected
        write_json(
            output / f"{name}.json",
            {
                "split": split,
                "paper_ids": selected,
                "seed": seed,
                "selection_rule": manifest.selection_rule,
                "pilot": True,
            },
        )
    manifest.selection_seed = seed
    write_json(output / "data_manifest.json", manifest)
