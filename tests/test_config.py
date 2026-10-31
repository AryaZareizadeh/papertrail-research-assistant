import json
import subprocess
import sys

import pytest
import yaml
from pydantic import ValidationError

from evidence_assistant.config import load_config


def write_config(tmp_path, **values):
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(values), encoding="utf-8")
    return path


def test_defaults_resolve_paths_relative_to_config(tmp_path):
    config = load_config(write_config(tmp_path))
    assert config.corpus_dir == tmp_path / "data" / "corpus"
    assert config.evaluation_dir == tmp_path / "data" / "evaluation"
    assert config.database_path == tmp_path / "artifacts" / "corpus.sqlite"
    assert config.top_k == 5
    assert config.generation_model is None


@pytest.mark.parametrize(
    "values",
    [
        {"top_k": 0},
        {"retrieval_method": "unknown"},
        {"corpus_dir": "data", "evaluation_dir": "data/answers"},
        {"corpus_dir": "data/answers", "evaluation_dir": "data"},
        {"raw_dir": "same", "corpus_dir": "same"},
        {"chunk_tokens": 32, "chunk_overlap_tokens": 32},
        {"top_k": 21, "candidate_k": 20},
        {"generator_context_tokens": 1000},
        {"generation_model": "some-model"},
        {"generation_tokenizer": "some-tokenizer"},
        {"top_ke": 8},
    ],
)
def test_invalid_configuration_is_rejected(tmp_path, values):
    with pytest.raises((ValidationError, ValueError)):
        load_config(write_config(tmp_path, **values))


def test_config_rejects_non_mapping_yaml(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("- something\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_config(path)


@pytest.mark.parametrize("values", [
    {"artifact_dir": "data/library"},
    {"artifact_dir": "custom/artifacts", "corpus_dir": "custom/library"},
    {"artifact_dir": "custom/artifacts", "report_dir": "custom/library/reports"},
])
def test_inferred_library_must_not_overlap_protected_paths(tmp_path, values):
    with pytest.raises(ValueError, match="overlap"):
        load_config(write_config(tmp_path, **values))


def test_doctor_reports_missing_artifacts_without_creating_them(tmp_path):
    path = write_config(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "evidence_assistant.cli", "doctor", "--config", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["artifacts"]["database"]["exists"] is False
    assert report["generation"]["ready"] is False
    assert not (tmp_path / "artifacts").exists()


def test_cli_invalid_config_exits_with_useful_message(tmp_path):
    path = write_config(tmp_path, top_k=0)
    result = subprocess.run(
        [sys.executable, "-m", "evidence_assistant.cli", "doctor", "--config", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "top_k" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_malformed_yaml_has_no_traceback(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("top_k: [broken", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "evidence_assistant.cli", "doctor", "--config", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_answer_cli_reports_missing_key_without_loading_models(tmp_path, monkeypatch):
    variable = "PAPERTRAIL_MISSING_KEY_TEST"
    monkeypatch.delenv(variable, raising=False)
    path = write_config(
        tmp_path,
        generation_model="openai/gpt-oss-20b",
        generation_tokenizer="openai/gpt-oss-20b",
        generation_api_key_env=variable,
        dotenv_path=str(tmp_path / "missing.env"),
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidence_assistant.cli",
            "answer",
            "--config",
            str(path),
            "--paper-id",
            "some-paper",
            "--question",
            "Which dataset?",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 3
    assert variable in result.stderr
    assert "Traceback" not in result.stderr
