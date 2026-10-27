"""HTTP-only UI boundary and safe source highlighting; no generation code."""

import hashlib
import html
import re
from urllib.parse import quote

import httpx
from pydantic import TypeAdapter, ValidationError

from evidence_assistant.schemas import AnswerResult, Citation, Paragraph, Record


class PaperInfo(Record):
    paper_id: str
    title: str
    sections: list[dict]


class UIError(Exception):
    def __init__(self, message, *, code="api_error", request_id=None):
        super().__init__(message)
        self.code = code
        self.request_id = request_id


MESSAGES = {
    "rate_limited": "The model service is rate limited. Wait before asking again.",
    "context_overflow": "This question exceeds the context budget. Try a shorter question.",
    "invalid_request": "Select a paper and enter a question of at most 2,000 characters.",
    "paper_not_found": "This paper is no longer available. Refresh the paper list.",
    "paragraph_not_found": "This original paragraph is no longer available.",
    "transport_error": "The API could not reach the model service. Try again later.",
    "missing_api_key": "The API needs its model credentials configured before it can answer.",
}


def _invalid_response():
    return UIError("The API did not return a valid response.", code="invalid_api_response")


class ApiClient:
    def __init__(self, base_url, *, transport=None):
        self.base_url = base_url.rstrip("/")
        self.transport = transport

    def _request(self, method, path, *, payload=None, timeout=15):
        try:
            if self.transport is None:
                with httpx.Client() as client:
                    response = client.request(
                        method, self.base_url + path, json=payload, timeout=timeout
                    )
            else:
                response = self.transport.request(
                    method, self.base_url + path, json=payload, timeout=timeout
                )
        except httpx.TimeoutException:
            raise UIError(
                "The API took too long to respond. The request may still be running.",
                code="request_timeout",
            ) from None
        except httpx.TransportError:
            raise UIError(
                "Could not connect to the API. Check that the API service is running.",
                code="api_unreachable",
            ) from None
        try:
            data = response.json()
        except ValueError:
            raise _invalid_response() from None
        if response.is_error:
            detail = data.get("detail", {}) if isinstance(data, dict) else {}
            detail = detail if isinstance(detail, dict) else {}
            code = detail.get("code")
            if not isinstance(code, str):
                code = None
            request_id = detail.get("request_id", response.headers.get("X-Request-ID"))
            if not isinstance(request_id, str) or not re.fullmatch("[a-f0-9]{32}", request_id):
                request_id = None
            message = MESSAGES.get(
                code, "The API could not complete this request. Try again later."
            )
            raise UIError(
                message, code=code if code in MESSAGES else "api_error", request_id=request_id
            )
        return data

    def papers(self):
        try:
            return TypeAdapter(list[PaperInfo]).validate_python(self._request("GET", "/papers"))
        except ValidationError:
            raise _invalid_response() from None

    def ready(self):
        data = self._request("GET", "/ready")
        if not isinstance(data, dict) or data.get("status") != "ready":
            raise _invalid_response()
        return data

    def ask(self, paper_id, question):
        data = self._request(
            "POST", "/questions", payload={"paper_id": paper_id, "question": question}, timeout=150
        )
        try:
            answer = AnswerResult.model_validate(data)
            if answer.paper_id != paper_id:
                raise _invalid_response()
            return answer
        except ValidationError:
            raise _invalid_response() from None

    def paragraph(self, paper_id, paragraph_id):
        data = self._request(
            "GET", f"/papers/{quote(paper_id, safe='')}/paragraphs/{quote(paragraph_id, safe='')}"
        )
        try:
            return Paragraph.model_validate(data)
        except ValidationError:
            raise _invalid_response() from None


def highlight_source(source: Paragraph, citation: Citation):
    start, end = citation.start_char, citation.end_char
    if (
        source.paper_id != citation.paper_id
        or source.paragraph_id != citation.paragraph_id
        or source.section_name != citation.section_name
        or not 0 <= start < end <= len(source.text)
        or source.text[start:end] != citation.quote
        or hashlib.sha256(source.text.encode()).hexdigest() != source.text_sha256
    ):
        raise UIError("The citation does not match the original source.", code="source_mismatch")
    return (
        html.escape(source.text[:start])
        + "<mark>"
        + html.escape(source.text[start:end])
        + "</mark>"
        + html.escape(source.text[end:])
    )
