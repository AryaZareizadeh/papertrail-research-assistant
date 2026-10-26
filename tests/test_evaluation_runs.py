import json

import pytest

from evidence_assistant.data import write_json, write_jsonl
from evidence_assistant.evaluation_runs import (
    freeze_run,
    load_cases,
    report_run,
    run_evaluation,
    validate_frozen_run,
)
from tests.test_evaluation import question, reference
from tests.test_generation import (
    completion,
    make_service,
    model_response,
)
from tests.test_generation import (
    generation_setup as generation_setup,
)
from tests.test_retrieval import retrieval_setup as retrieval_setup


@pytest.fixture
def evaluation_setup(generation_setup):
    config, index = generation_setup
    base = config.artifact_dir.parent
    config = config.model_copy(
        update={"evaluation_dir": base / "evaluation", "manifest_dir": base / "manifests"}
    )
    q = question("q1", [reference("a", ["Dataset Alpha is used for evaluation."])])
    q.paper_id = "selected"
    write_jsonl(config.evaluation_dir / "questions.jsonl", [q])
    for name in ("data_manifest.json", "validation_pilot.json", "test_pilot.json"):
        write_json(config.manifest_dir / name, {"split": "train", "paper_ids": ["selected"]})
    for name in ("generation_tokenizer.json", "generation_token_calibration.json"):
        write_json(config.artifact_dir / name, {"fixture": True})
    return config, index


def test_freeze_rejects_config_selection_source_and_policy_changes(evaluation_setup, tmp_path):
    config, _ = evaluation_setup
    frozen = tmp_path / "frozen.json"
    freeze_run(config, frozen)
    validate_frozen_run(config, frozen)
    changed = config.model_copy(update={"max_evidence_tokens": config.max_evidence_tokens + 1})
    with pytest.raises(ValueError, match="differ"):
        validate_frozen_run(changed, frozen)
    write_json(config.manifest_dir / "test_pilot.json", {"changed": True})
    with pytest.raises(ValueError, match="differ"):
        validate_frozen_run(config, frozen)
    with pytest.raises(ValueError, match="exists"):
        freeze_run(config, frozen)


def test_selection_rejects_wrong_split_unknown_papers_and_final_test_without_freeze(
    evaluation_setup,
):
    config, _ = evaluation_setup
    manifest = config.manifest_dir / "validation_pilot.json"
    assert len(load_cases(config, "train", manifest)) == 1
    with pytest.raises(ValueError, match="split"):
        load_cases(config, "validation", manifest)
    write_json(manifest, {"split": "train", "paper_ids": ["missing"]})
    with pytest.raises(ValueError, match="indexed"):
        load_cases(config, "train", manifest)
    with pytest.raises(ValueError, match="frozen"):
        run_evaluation(config, "test", None, ["hybrid"], qa=True)


def test_saved_context_is_shared_and_resume_does_not_call_provider_twice(
    evaluation_setup, tmp_path
):
    config, index = evaluation_setup
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return model_response(completion())

    service = make_service((config, index), handler)
    manifest = config.manifest_dir / "validation_pilot.json"
    run_dir = tmp_path / "evaluation"
    result = run_evaluation(
        config,
        "train",
        manifest,
        ["hybrid"],
        qa=True,
        output=run_dir,
        service=service,
        interval_seconds=0,
    )
    assert len(calls) == 1
    rows = [json.loads(line) for line in (run_dir / "predictions.jsonl").read_text().splitlines()]
    assert rows[0]["supplied_chunk_ids"] == rows[0]["result"]["retrieved_chunk_ids"]
    assert rows[0]["supplied_passages"]
    assert result["methods"]["hybrid"]["answers"]["whole_selected"]["selected_questions"] == 1
    run_evaluation(
        config,
        "train",
        manifest,
        ["hybrid"],
        qa=True,
        output=run_dir,
        service=service,
        interval_seconds=0,
    )
    assert len(calls) == 1
    with pytest.raises(ValueError, match="differ"):
        run_evaluation(
            config.model_copy(update={"prompt_version": "changed"}),
            "train",
            manifest,
            ["hybrid"],
            qa=True,
            output=run_dir,
            service=service,
        )


def test_provider_error_keeps_selected_case_and_is_not_encoded_as_unanswerable(
    evaluation_setup, tmp_path
):
    config, index = evaluation_setup
    import httpx

    service = make_service((config, index), lambda request: httpx.Response(429))
    output = tmp_path / "errors"
    result = run_evaluation(
        config,
        "train",
        config.manifest_dir / "validation_pilot.json",
        ["hybrid"],
        qa=True,
        output=output,
        service=service,
        interval_seconds=0,
    )
    assert (
        result["methods"]["hybrid"]["answers"]["whole_selected"]["system_error_rate"]["value"] == 1
    )
    assert (output / "hybrid_official_predictions.jsonl").read_text() == ""
    row = json.loads((output / "predictions.jsonl").read_text())
    assert row["status"] == "error"
    assert row["error_code"] == "rate_limited"
    assert row["supplied_passages"]  # Recoverable fixed-context comparison even after a failure.


def test_requested_dense_evaluation_loads_encoder_even_with_bm25_default(
    evaluation_setup, tmp_path, monkeypatch
):
    config, index = evaluation_setup
    config = config.model_copy(update={"retrieval_method": "bm25"})
    calls = []
    service = make_service((config, index), lambda req: model_response(completion()))

    def build(config, method=None):
        calls.append(method)
        return service

    monkeypatch.setattr("evidence_assistant.service.build_answer_service", build)
    run_evaluation(
        config,
        "train",
        config.manifest_dir / "validation_pilot.json",
        ["dense"],
        qa=True,
        output=tmp_path / "dense",
        interval_seconds=0,
    )
    assert calls == ["dense"]


@pytest.mark.parametrize("change", ["references", "paragraphs", "scoring"])
def test_report_rejects_changed_scoring_inputs_or_identity(evaluation_setup, tmp_path, change):
    config, index = evaluation_setup
    service = make_service((config, index), lambda req: model_response(completion()))
    output = tmp_path / "audit"
    run_evaluation(
        config,
        "train",
        config.manifest_dir / "validation_pilot.json",
        ["hybrid"],
        qa=True,
        output=output,
        service=service,
        interval_seconds=0,
    )
    if change == "scoring":
        path = output / "manifest.json"
        record = json.loads(path.read_text())
        record["scoring_identity"] = {"changed": True}
        write_json(path, record)
    else:
        path = output / f"{change}.jsonl"
        path.write_text(path.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="scoring|changed"):
        report_run(output)


def test_frozen_test_gate_allows_one_run_and_resume_of_synthetic_test_selection(
    evaluation_setup, tmp_path
):
    import sqlite3
    from contextlib import closing

    config, index = evaluation_setup
    # Change only this isolated synthetic fixture's label; never inspect real test answers.
    with closing(sqlite3.connect(config.database_path)) as db, db:
        paper = json.loads(
            db.execute("SELECT record FROM papers WHERE paper_id='selected'").fetchone()[0]
        )
        paper["split"] = "test"
        db.execute(
            "UPDATE papers SET split=?, record=? WHERE paper_id='selected'",
            ("test", json.dumps(paper)),
        )
    manifest = config.manifest_dir / "test_pilot.json"
    write_json(manifest, {"split": "test", "paper_ids": ["selected"]})
    frozen, output = tmp_path / "frozen.json", tmp_path / "final"
    freeze_run(config, frozen)
    service = make_service((config, index), lambda req: model_response(completion()))
    kwargs = dict(qa=True, frozen_run_manifest=frozen, service=service, interval_seconds=0)
    with pytest.raises(ValueError, match="explicit"):
        run_evaluation(config, "test", None, ["hybrid"], output=output, **kwargs)
    with pytest.raises(ValueError, match="limit"):
        run_evaluation(config, "test", manifest, ["hybrid"], output=output, limit=1, **kwargs)
    run_evaluation(config, "test", manifest, ["hybrid"], output=output, **kwargs)
    # Resuming the completed directory reads its saved prediction without a new call.
    service.adapter.generate = lambda *args: pytest.fail("A completed test must not regenerate")
    run_evaluation(config, "test", manifest, ["hybrid"], output=output, **kwargs)
    another_frozen = tmp_path / "renamed-frozen.json"
    freeze_run(config, another_frozen)
    kwargs["frozen_run_manifest"] = another_frozen
    with pytest.raises(ValueError, match="already started"):
        run_evaluation(config, "test", manifest, ["hybrid"], output=tmp_path / "again", **kwargs)
