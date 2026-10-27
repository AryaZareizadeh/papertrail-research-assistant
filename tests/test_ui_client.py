"""UI transport and source rendering mechanics; no hosted generation."""

import hashlib

import httpx
import pytest

from evidence_assistant.schemas import Citation, Paragraph
from evidence_assistant.ui_client import ApiClient, UIError, highlight_source


def test_source_highlight_uses_unicode_offsets_and_escapes_original_text():
    text = "😀 <script>x</script> Source & context."
    start, end = text.index("Source"), text.index("Source") + len("Source")
    source = Paragraph(
        paper_id="paper",
        paragraph_id="p1",
        section_index=0,
        section_name="Methods",
        paragraph_index=0,
        text=text,
        text_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
    citation = Citation(
        chunk_id="c1",
        paper_id="paper",
        paragraph_id="p1",
        section_name="Methods",
        start_char=start,
        end_char=end,
        quote="Source",
    )
    result = highlight_source(source, citation)
    assert "<mark>Source</mark>" in result
    assert "&lt;script&gt;x&lt;/script&gt;" in result
    assert "&amp; context." in result and "😀" in result
    with pytest.raises(UIError, match="match"):
        highlight_source(source, citation.model_copy(update={"quote": "Wrong"}))
    with pytest.raises(UIError, match="match"):
        highlight_source(source, citation.model_copy(update={"paper_id": "other"}))


def test_transport_preserves_error_identity_without_retrying_or_leaking_body():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            503,
            json={
                "detail": {
                    "code": "rate_limited",
                    "message": "SECRET_RAW_MESSAGE",
                    "request_id": "a" * 32,
                },
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
        client = ApiClient("http://example.test", transport=transport)
        with pytest.raises(UIError) as caught:
            client.ask("paper", "Which dataset?")
    assert len(calls) == 1
    assert caught.value.code == "rate_limited"
    assert caught.value.request_id == "a" * 32
    assert "SECRET_RAW_MESSAGE" not in str(caught.value)


def test_bad_api_response_and_network_failure_are_controlled():
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, text="oops"))
    ) as transport:
        with pytest.raises(UIError, match="valid response"):
            ApiClient("http://example.test", transport=transport).papers()

    def unavailable(request):
        raise httpx.ConnectError("SECRET_TRANSPORT_TRACE", request=request)

    with httpx.Client(transport=httpx.MockTransport(unavailable)) as transport:
        with pytest.raises(UIError, match="connect") as caught:
            ApiClient("http://example.test", transport=transport).papers()
        assert "SECRET_TRANSPORT_TRACE" not in str(caught.value)


@pytest.mark.parametrize("code", [[], {}, None])
def test_malformed_error_codes_use_a_controlled_generic_error(code):
    transport = httpx.MockTransport(lambda _: httpx.Response(503, json={"detail": {"code": code}}))
    with httpx.Client(transport=transport) as client:
        with pytest.raises(UIError) as caught:
            ApiClient("http://example.test", transport=client).papers()
    assert caught.value.code == "api_error"
