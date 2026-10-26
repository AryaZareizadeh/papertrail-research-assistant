import json
import os
from pathlib import Path

import pytest

# Keep subprocess CLI checks importable before an editable install finishes.
os.environ["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")


@pytest.fixture
def qasper_release(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    for split, filename in (
        ("train", "qasper-train-v0.3.json"),
        ("validation", "qasper-dev-v0.3.json"),
        ("test", "qasper-test-v0.3.json"),
    ):
        paper_id = f"paper-{split}"
        paragraph = "We evaluate on Dataset Alpha using accuracy."
        paper = {
            "title": f"A paper for {split}",
            "abstract": "This paper studies evaluation.",
            "full_text": [{"section_name": "Experiments", "paragraphs": [paragraph, paragraph]}],
            "qas": [
                {
                    "question_id": f"q-{split}",
                    "question": "Which dataset is used?",
                    "answers": [
                        {
                            "answer": {
                                "unanswerable": False,
                                "extractive_spans": [],
                                "free_form_answer": "GOLD_SECRET_DO_NOT_INDEX",
                                "yes_no": None,
                                "evidence": [paragraph],
                                "highlighted_evidence": ["Dataset Alpha"],
                            }
                        },
                        {
                            "answer": {
                                "unanswerable": True,
                                "extractive_spans": [],
                                "free_form_answer": "",
                                "yes_no": None,
                                "evidence": [],
                                "highlighted_evidence": [],
                            }
                        },
                    ],
                }
            ],
        }
        (raw / filename).write_text(json.dumps({paper_id: paper}), encoding="utf-8")
    return raw
