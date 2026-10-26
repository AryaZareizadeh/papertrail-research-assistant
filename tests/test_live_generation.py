import os
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("PAPERTRAIL_LIVE_GROQ") != "1",
        reason="Set PAPERTRAIL_LIVE_GROQ=1 to enable real hosted-model calls",
    ),
]


def test_live_hosted_answer_has_exact_source_citations():
    from evidence_assistant.config import load_config
    from evidence_assistant.service import answer_question, build_answer_service
    from evidence_assistant.store import get_paragraph

    config = load_config(Path(__file__).resolve().parents[1] / "config.yaml")
    service = build_answer_service(config)
    result = answer_question("What word embeddings were used?", "1911.07228", "hybrid", service)
    assert result.status == "answered"
    assert result.claims and result.citations
    for citation in result.citations:
        source = get_paragraph(config.database_path, citation.paper_id, citation.paragraph_id)
        assert source.text[citation.start_char : citation.end_char] == citation.quote
