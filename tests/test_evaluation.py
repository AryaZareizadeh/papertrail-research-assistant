"""Scoring fixtures are synthetic; they do not estimate benchmark quality."""

import pytest

from evidence_assistant.data import text_hash
from evidence_assistant.evaluation import (
    EvaluationPolicy,
    answerability,
    evaluate_answers,
    evaluate_retrieval,
    map_evidence,
    official_prediction,
    question_flags,
)
from evidence_assistant.schemas import AnswerReference, GoldQuestion, Paragraph


def paragraph(pid, text, paper="paper"):
    return Paragraph(
        paragraph_id=pid,
        paper_id=paper,
        section_index=0,
        section_name="Methods",
        paragraph_index=0,
        text=text,
        text_sha256=text_hash(text),
    )


def reference(aid, evidence=(), *, unanswerable=False, answer="Alpha"):
    return AnswerReference(
        annotation_id=aid,
        answer_type="abstractive",
        answer_text=answer,
        unanswerable=unanswerable,
        evidence=list(evidence),
        highlighted_evidence=["highlight only"],
    )


def question(qid="q", refs=None):
    return GoldQuestion(
        question_id=qid,
        paper_id="paper",
        question="Which dataset?",
        references=refs or [reference("a", ["Alpha", "Beta"])],
        annotation_disagreement=False,
        uses_float_evidence=False,
    )


def test_mapping_preserves_positions_whitespace_and_unmatched_categories():
    source = [
        paragraph("p1", "Alpha"),
        paragraph("p2", "Alpha"),
        paragraph("p3", "Beta\n  result"),
        paragraph("foreign", "Gamma", "other"),
    ]
    q = question(
        refs=[reference("a", ["Alpha", "Beta result", "FLOAT SELECTED: table 1", "Gamma", "Alphx"])]
    )
    mapping = map_evidence(q, source)
    items = mapping.annotations[0].items
    assert items[0].candidate_paragraph_ids == ["p1", "p2"]
    assert [i.status for i in items] == ["exact", "whitespace", "float", "unmapped", "unmapped"]
    assert "highlight only" not in [i.original for i in items]


@pytest.mark.parametrize(
    "ids,hit,recall,complete",
    [
        (["p1", "p2"], 1, 1, 1),
        (["p1", "p1"], 1, 0.5, 0),
        (["wrong"], 0, 0, 0),
        ([], 0, 0, 0),
    ],
)
def test_paragraph_metrics_perfect_partial_wrong_and_empty(ids, hit, recall, complete):
    q = question()
    source = [paragraph("p1", "Alpha"), paragraph("p2", "Beta")]
    metrics = evaluate_retrieval(
        {"q": {"supplied_paragraph_ids": ids}}, [q], source, EvaluationPolicy()
    )["whole_selected"]
    for name, expected in [
        ("evidence_hit_at_5", hit),
        ("evidence_recall_at_5", recall),
        ("complete_evidence_coverage", complete),
    ]:
        assert metrics[name]["value"] == expected
        assert metrics[name]["denominator"] == 1


def test_best_annotator_and_duplicate_position_are_alternatives_not_a_union():
    q = question(refs=[reference("a", ["Alpha", "Beta"]), reference("b", ["Gamma"])])
    source = [
        paragraph("a1", "Alpha"),
        paragraph("a2", "Alpha"),
        paragraph("b", "Beta"),
        paragraph("g", "Gamma"),
    ]
    m = evaluate_retrieval(
        {"q": {"supplied_paragraph_ids": ["g"]}}, [q], source, EvaluationPolicy()
    )["whole_selected"]
    assert m["evidence_recall_at_5"]["value"] == 1
    assert m["complete_evidence_coverage"]["value"] == 1
    q.references = [reference("a", ["Alpha"])]
    m = evaluate_retrieval(
        {"q": {"supplied_paragraph_ids": ["a2"]}}, [q], source, EvaluationPolicy()
    )["whole_selected"]
    assert m["complete_evidence_coverage"]["value"] == 1


def test_empty_evidence_is_not_unanswerability_and_any_float_excludes_strict_slice():
    empty = question(refs=[reference("a")])
    assert answerability(empty) == "consensus_answerable"
    assert "absence_based_answer" in question_flags(empty, map_evidence(empty, []))
    mixed = question(refs=[reference("a", ["Alpha"]), reference("b", ["FLOAT SELECTED: x"])])
    source = [paragraph("p1", "Alpha")]
    m = evaluate_retrieval({}, [mixed], source, EvaluationPolicy())
    assert m["strict_text_only"]["evidence_hit_at_5"]["denominator"] == 0
    assert m["whole_selected"]["evidence_hit_at_5"]["denominator"] == 1
    empty_m = evaluate_retrieval({}, [empty], [], EvaluationPolicy())
    assert empty_m["whole_selected"]["evidence_recall_at_5"]["excluded_counts"] == {
        "no_complete_mapped_positive_reference": 1
    }


def test_missing_and_provider_error_are_zero_and_never_successful_refusals():
    refs = [
        question("good", [reference("a", ["Alpha"])]),
        question("false_refusal", [reference("a", ["Alpha"])]),
        question("refusal", [reference("a", unanswerable=True)]),
        question("error", [reference("a", unanswerable=True)]),
        question("missing", [reference("a", unanswerable=True)]),
        question("mixed", [reference("a"), reference("b", unanswerable=True)]),
    ]
    predictions = {
        "good": {
            "status": "answered",
            "result": {"claims": [{"text": "Alpha"}], "citations": []},
            "latency_ms": 10,
        },
        "false_refusal": {"status": "insufficient_evidence"},
        "refusal": {"status": "insufficient_evidence"},
        "error": {"status": "error", "error_code": "rate_limit"},
        "mixed": {"status": "insufficient_evidence"},
    }
    m = evaluate_answers(predictions, refs, [], EvaluationPolicy())["whole_selected"]
    assert m["official"]["Answer F1"] == pytest.approx(3 / 6)
    assert m["official"]["Missing predictions"] == 2
    assert m["abstention_precision"]["value"] == 0.5
    assert m["unanswerable_recall"]["value"] == pytest.approx(1 / 3)
    assert m["false_refusal_rate"]["value"] == 0.5
    assert m["system_error_rate"]["value"] == pytest.approx(1 / 6)
    assert m["missing_prediction_rate"]["value"] == pytest.approx(1 / 6)
    assert m["answerability_counts"]["mixed"] == 1


def test_official_adapter_keeps_original_paragraphs_and_errors_out_of_jsonl():
    source = [paragraph("p1", "Original\ntext")]
    record = {
        "status": "answered",
        "result": {
            "claims": [{"text": "Yes."}],
            "citations": [{"paragraph_id": "p1"}, {"paragraph_id": "p1"}],
        },
    }
    assert official_prediction("q", record, source) == {
        "question_id": "q",
        "predicted_answer": "Yes.",
        "predicted_evidence": ["Original\ntext"],
    }
    assert official_prediction("q", {"status": "error"}, source) is None
    assert (
        official_prediction("q", {"status": "insufficient_evidence"}, source)["predicted_answer"]
        == "Unanswerable"
    )


def test_citation_validity_checks_source_span_and_supplied_membership():
    q, source = question(refs=[reference("a", ["Alpha"])]), [paragraph("p", "Alpha")]
    citation = {
        "chunk_id": "c",
        "paper_id": "paper",
        "paragraph_id": "p",
        "start_char": 0,
        "end_char": 5,
        "quote": "Alpha",
    }
    record = {
        "status": "answered",
        "supplied_chunk_ids": ["c"],
        "supplied_passages": [
            {
                "chunk_id": "c",
                "paper_id": "paper",
                "paragraph_id": "p",
                "start_char": 0,
                "end_char": 5,
                "text": "Alpha",
            }
        ],
        "result": {
            "claims": [{"text": "Alpha", "citation_chunk_ids": ["c"]}],
            "citations": [
                citation,
                {**citation, "chunk_id": "foreign"},
                {**citation, "quote": "invented"},
            ],
        },
    }
    m = evaluate_answers({"q": record}, [q], source, EvaluationPolicy())["whole_selected"]
    assert m["citation_validity"]["value"] == pytest.approx(1 / 3)
    assert m["citation_validity"]["denominator"] == 3


def test_citation_id_cannot_be_rebound_to_a_different_source_passage():
    from evidence_assistant.evaluation import _citation_counts

    source = [paragraph("p1", "Alpha"), paragraph("p2", "Beta")]
    record = {
        "supplied_chunk_ids": ["c1"],
        "supplied_passages": [
            {
                "chunk_id": "c1",
                "paper_id": "paper",
                "paragraph_id": "p1",
                "start_char": 0,
                "end_char": 5,
                "text": "Alpha",
            }
        ],
        "result": {
            "citations": [
                {
                    "chunk_id": "c1",
                    "paper_id": "paper",
                    "paragraph_id": "p2",
                    "start_char": 0,
                    "end_char": 4,
                    "quote": "Beta",
                }
            ]
        },
    }
    assert _citation_counts(question(), record, source) == (0, 1)


def test_official_source_is_pinned_and_multiple_reference_f1_is_used():
    from evidence_assistant.evaluation import official_source_identity

    assert official_source_identity()["sha256"] == (
        "781aba7cd8e524bef4f0a1b4bf3504e5b02cb1d8d5bf32a8f0a89dfa83e86bfe"
    )
    q = question(refs=[reference("a", answer="Beta"), reference("b", answer="The Alpha")])
    pred = {"q": {"status": "answered", "result": {"claims": [{"text": "Alpha"}], "citations": []}}}
    assert (
        evaluate_answers(pred, [q], [], EvaluationPolicy())["whole_selected"]["official"][
            "Answer F1"
        ]
        == 1
    )
