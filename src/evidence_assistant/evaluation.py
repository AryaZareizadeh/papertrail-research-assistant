"""Offline scoring only. Gold annotations never enter the application service."""

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from evidence_assistant._vendor import qasper_evaluator as official
from evidence_assistant.data import file_hash, text_hash
from evidence_assistant.schemas import (
    AnnotationMapping,
    EvidenceItem,
    EvidenceMapping,
    GoldQuestion,
    Paragraph,
)


@dataclass(frozen=True)
class EvaluationPolicy:
    version: str = "qasper-text-v1"
    top_k: int = 5
    strict_exclusions: tuple = ("float_evidence", "unmapped_evidence", "absence_based_answer")
    whitespace_fallback: str = "split-join-only"
    retrieval_references: str = "best-complete-mapped-positive-annotator"
    abstention_labels: str = "consensus-only-mixed-reported-separately"

    def snapshot(self):
        return json.loads(json.dumps(asdict(self)))

    @property
    def sha256(self):
        return text_hash(json.dumps(self.snapshot(), sort_keys=True))


def official_source_identity() -> dict:
    root = Path(__file__).parent / "_vendor"
    identity = json.loads((root / "provenance.json").read_text("utf-8"))
    if file_hash(root / "qasper_evaluator.py") != identity["sha256"]:
        raise ValueError("Pinned official evaluator source changed")
    return identity


def map_evidence(question: GoldQuestion, paragraphs: list[Paragraph]) -> EvidenceMapping:
    exact, whitespace = {}, {}
    for p in paragraphs:
        if p.paper_id == question.paper_id:
            exact.setdefault(p.text, []).append(p.paragraph_id)
            whitespace.setdefault(" ".join(p.text.split()), []).append(p.paragraph_id)
    annotations = []
    for ref in question.references:
        items = []
        for text in dict.fromkeys(ref.evidence):
            if text.startswith("FLOAT SELECTED"):
                ids, status = [], "float"
            elif text in exact:
                ids, status = exact[text], "exact"
            elif text.strip() and " ".join(text.split()) in whitespace:
                ids, status = whitespace[" ".join(text.split())], "whitespace"
            else:
                ids, status = [], "unmapped"
            items.append(
                EvidenceItem(
                    original=text,
                    candidate_paragraph_ids=sorted(ids),
                    status=status,
                    match_method=status,
                )
            )
        annotations.append(AnnotationMapping(annotation_id=ref.annotation_id, items=items))
    return EvidenceMapping(question_id=question.question_id, annotations=annotations)


def answerability(question: GoldQuestion) -> str:
    labels = {r.unanswerable for r in question.references}
    if not labels:
        raise ValueError(f"Question has no retained annotations: {question.question_id}")
    if len(labels) > 1:
        return "mixed"
    return "consensus_unanswerable" if True in labels else "consensus_answerable"


def question_flags(question: GoldQuestion, mapping: EvidenceMapping) -> list[str]:
    flags = set()
    for ref, annotation in zip(question.references, mapping.annotations, strict=True):
        if any(i.status == "float" for i in annotation.items):
            flags.add("float_evidence")
        if any(i.status == "unmapped" for i in annotation.items):
            flags.add("unmapped_evidence")
        if not ref.unanswerable and not annotation.items:
            flags.add("absence_based_answer")
    return sorted(flags)


def _metric(numerator, denominator, excluded=None):
    return {
        "value": numerator / denominator if denominator else None,
        "numerator": numerator,
        "denominator": denominator,
        "excluded_counts": dict(excluded or {}),
    }


def _slices(references, paragraphs, policy):
    mapped = [(q, map_evidence(q, paragraphs)) for q in references]
    strict = [
        (q, m)
        for q, m in mapped
        if not set(question_flags(q, m)).intersection(policy.strict_exclusions)
    ]
    return {"whole_selected": mapped, "strict_text_only": strict}


def eligibility_summary(references, paragraphs, policy):
    by_split = Counter()
    records = []
    for q in references:
        mapping = map_evidence(q, paragraphs)
        flags = question_flags(q, mapping)
        eligible = not set(flags).intersection(policy.strict_exclusions)
        by_split.update(flags)
        records.append(
            {
                "question_id": q.question_id,
                "paper_id": q.paper_id,
                "answerability": answerability(q),
                "flags": flags,
                "strict_text_only": eligible,
                "mapping": mapping.model_dump(),
                "highlighted_evidence": {
                    r.annotation_id: r.highlighted_evidence for r in q.references
                },
            }
        )
    return {
        "questions": len(records),
        "strict_text_only": sum(r["strict_text_only"] for r in records),
        "overlapping_exclusion_reasons": dict(by_split),
        "records": records,
    }


def evaluate_retrieval(predictions, references, paragraphs, policy):
    output = {}
    for name, cases in _slices(references, paragraphs, policy).items():
        hit = recall = complete = 0
        denominator, excluded = 0, Counter()
        for q, mapping in cases:
            valid_refs = []
            for ref, annotation in zip(q.references, mapping.annotations, strict=True):
                if ref.unanswerable or not annotation.items:
                    continue
                if any(not i.candidate_paragraph_ids for i in annotation.items):
                    continue
                # Duplicate/whitespace-equivalent evidence items earn credit once.
                valid_refs.append(set(tuple(i.candidate_paragraph_ids) for i in annotation.items))
            if not valid_refs:
                excluded["no_complete_mapped_positive_reference"] += 1
                continue
            denominator += 1
            record = predictions.get(q.question_id, {})
            covered = set(record.get("supplied_paragraph_ids", []))
            scores = [
                sum(bool(covered.intersection(item)) for item in items) / len(items)
                for items in valid_refs
            ]
            score = max(scores)
            hit += score > 0
            recall += score
            complete += score == 1
        output[name] = {
            "selected_questions": len(cases),
            "evidence_hit_at_5": _metric(hit, denominator, excluded),
            "evidence_recall_at_5": _metric(recall, denominator, excluded),
            "complete_evidence_coverage": _metric(complete, denominator, excluded),
        }
    return output


def official_prediction(question_id, record, paragraphs):
    if record.get("status") not in {"answered", "insufficient_evidence"}:
        return None  # Official scorer assigns missing/error predictions zero.
    result = record.get("result", {})
    by_id = {p.paragraph_id: p for p in paragraphs}
    evidence = list(
        dict.fromkeys(
            by_id[c["paragraph_id"]].text
            for c in result.get("citations", [])
            if c["paragraph_id"] in by_id
        )
    )
    return {
        "question_id": question_id,
        "predicted_answer": "Unanswerable"
        if record["status"] == "insufficient_evidence"
        else " ".join(c["text"] for c in result.get("claims", [])),
        "predicted_evidence": evidence,
    }


def _official_references(questions):
    gold = {}
    for q in questions:
        gold[q.question_id] = []
        for r in q.references:
            # Preserve upstream answer priority from the original annotation.
            if r.raw_answer:
                raw = {
                    "p": {
                        "qas": [
                            {"question_id": q.question_id, "answers": [{"answer": r.raw_answer}]}
                        ]
                    }
                }
                ref = official.get_answers_and_evidence(raw, False)[q.question_id][0]
            else:
                ref = {
                    "answer": "Unanswerable" if r.unanswerable else r.answer_text,
                    "evidence": [] if r.unanswerable else r.evidence,
                    "type": "none" if r.unanswerable else r.answer_type,
                }
            gold[q.question_id].append(ref)
    return gold


def _citation_counts(q, record, paragraphs):
    by_id = {p.paragraph_id: p for p in paragraphs if p.paper_id == q.paper_id}
    supplied = set(record.get("supplied_chunk_ids", []))
    passages = {p["chunk_id"]: p for p in record.get("supplied_passages", [])}
    citations = record.get("result", {}).get("citations", [])
    valid = 0
    for c in citations:
        p = by_id.get(c.get("paragraph_id"))
        chunk = passages.get(c.get("chunk_id"))
        start, end = c.get("start_char", -1), c.get("end_char", -1)
        valid += bool(
            p
            and chunk
            and c.get("paper_id") == q.paper_id
            and c.get("chunk_id") in supplied
            and all(
                c.get(k) == chunk.get(k)
                for k in ("paper_id", "paragraph_id", "start_char", "end_char")
            )
            and c.get("quote") == chunk.get("text")
            and type(start) is int
            and type(end) is int
            and 0 <= start < end <= len(p.text)
            and p.text[start:end] == c.get("quote")
        )
    return valid, len(citations)


def evaluate_answers(predictions, references, paragraphs, policy):
    official_source_identity()
    output = {}
    for name, cases in _slices(references, paragraphs, policy).items():
        questions = [q for q, _ in cases]
        gold = _official_references(questions)
        adapter = [
            official_prediction(q.question_id, predictions.get(q.question_id, {}), paragraphs)
            for q in questions
        ]
        adapted = {
            p["question_id"]: {"answer": p["predicted_answer"], "evidence": p["predicted_evidence"]}
            for p in adapter
            if p is not None
        }
        labels = Counter(answerability(q) for q in questions)
        counts, valid, citations, latency = Counter(), 0, 0, []
        for q in questions:
            record = predictions.get(q.question_id, {})
            status, label = record.get("status", "missing"), answerability(q)
            counts[status] += 1
            if status == "insufficient_evidence" and label != "mixed":
                counts["consensus_refusals"] += 1
                counts["correct_refusals"] += label == "consensus_unanswerable"
                counts["false_refusals"] += label == "consensus_answerable"
            v, n = _citation_counts(q, record, paragraphs)
            valid, citations = valid + v, citations + n
            if "latency_ms" in record:
                latency.append(record["latency_ms"])
        output[name] = {
            "selected_questions": len(questions),
            "answerability_counts": dict(labels),
            "official": official.evaluate(gold, adapted),
            "citation_validity": _metric(valid, citations),
            "answer_coverage": _metric(counts["answered"], len(questions)),
            "abstention_precision": _metric(
                counts["correct_refusals"], counts["consensus_refusals"]
            ),
            "unanswerable_recall": _metric(
                counts["correct_refusals"], labels["consensus_unanswerable"]
            ),
            "false_refusal_rate": _metric(counts["false_refusals"], labels["consensus_answerable"]),
            "system_error_rate": _metric(counts["error"], len(questions)),
            "missing_prediction_rate": _metric(counts["missing"], len(questions)),
            "warm_latency_ms": {
                "p50": float(np.percentile(latency, 50)) if latency else None,
                "p95": float(np.percentile(latency, 95)) if latency else None,
                "denominator": len(latency),
            },
            "claim_support": {"value": None, "note": "Requires a separate human audit"},
        }
    return output
