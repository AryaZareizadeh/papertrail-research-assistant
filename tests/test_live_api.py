"""Opt-in training-paper smoke through the real API and hosted model."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evidence_assistant.api import create_app
from evidence_assistant.config import load_config

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("PAPERTRAIL_LIVE_API") != "1",
        reason="Set PAPERTRAIL_LIVE_API=1 to enable the real hosted API smoke",
    ),
]


def test_live_api_answer_resolves_to_original_training_paragraphs():
    path = Path(os.environ.get("PAPERTRAIL_CONFIG", "config.yaml"))
    config = load_config(path)
    with TestClient(create_app(config=config)) as client:
        assert client.get("/ready").status_code == 200
        response = client.post(
            "/questions",
            json={"paper_id": "1911.07228", "question": "What word embeddings were used?"},
        )
        assert response.status_code == 200, response.text
        answer = response.json()
        assert answer["status"] == "answered"
        assert answer["method"] == config.retrieval_method
        assert answer["request_id"] == response.headers["X-Request-ID"]
        assert answer["claims"] and answer["citations"]
        for citation in answer["citations"]:
            source = client.get(
                f"/papers/{citation['paper_id']}/paragraphs/{citation['paragraph_id']}"
            )
            assert source.status_code == 200
            text = source.json()["text"]
            assert text[citation["start_char"] : citation["end_char"]] == citation["quote"]
