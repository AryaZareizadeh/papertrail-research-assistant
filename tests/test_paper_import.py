"""PDF and arXiv boundaries: synthetic documents and transports only."""

from importlib import import_module
from io import BytesIO

import httpx
import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


def pdf_bytes(text="Dataset Alpha uses accuracy.", *, encrypted=False, blank=False):
    writer = PdfWriter()
    page = writer.add_blank_page(width=600, height=800)
    if not blank:
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})
        })
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode("ascii"))
        page[NameObject("/Contents")] = writer._add_object(stream)
    writer.add_metadata({"/Title": "A synthetic paper"})
    if encrypted:
        writer.encrypt("secret")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_extract_preserves_pages_and_pdf_identity():
    module = import_module("evidence_assistant.paper_import")
    data = pdf_bytes()
    result = module.extract_pdf(data, filename="../../paper.pdf")
    assert result.title == "A synthetic paper"
    assert result.pages == 1
    assert result.paragraphs[0].section_name == "Page 1"
    assert result.paragraphs[0].text == "Dataset Alpha uses accuracy."
    assert len(result.pdf_sha256) == 64
    assert result.paper_id == "pdf-" + result.pdf_sha256


@pytest.mark.parametrize("kind", ["bad", "blank", "encrypted", "large"])
def test_unusable_pdf_is_rejected(kind):
    module = import_module("evidence_assistant.paper_import")
    data = {
        "bad": b"not a pdf", "blank": pdf_bytes(blank=True),
        "encrypted": pdf_bytes(encrypted=True), "large": b"%PDF-" + b"x" * module.MAX_PDF_BYTES,
    }[kind]
    with pytest.raises(module.ImportProblem):
        module.extract_pdf(data, filename="test.pdf")


@pytest.mark.parametrize("url,identifier", [
    ("https://arxiv.org/abs/2401.12345", "2401.12345"),
    ("https://arxiv.org/pdf/2401.12345v2.pdf", "2401.12345v2"),
    ("hep-th/9901001", "hep-th/9901001"),
])
def test_arxiv_input_normalizes_to_identifier(url, identifier):
    module = import_module("evidence_assistant.paper_import")
    assert module.arxiv_identifier(url) == identifier


@pytest.mark.parametrize("url", [
    "https://evil.test/abs/2401.12345", "https://arxiv.org.evil.test/abs/2401.12345",
    "http://127.0.0.1/paper", "https://user@arxiv.org/abs/2401.12345",
    "https://arxiv.org:444/abs/2401.12345", "https://arxiv.org/abs/../../secret",
    "https://arxiv.org/abs/2401.12345?target=localhost",
])
def test_arxiv_rejects_other_hosts_and_ambiguous_urls(url):
    module = import_module("evidence_assistant.paper_import")
    with pytest.raises(module.ImportProblem):
        module.arxiv_identifier(url)


def test_arxiv_download_and_redirect_boundary():
    module = import_module("evidence_assistant.paper_import")
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(200, content=pdf_bytes(), headers={"content-type": "application/pdf"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        data, origin = module.fetch_arxiv("2401.12345v2", client=client)
    assert data.startswith(b"%PDF-")
    assert origin == "https://arxiv.org/abs/2401.12345v2"
    assert seen == ["https://arxiv.org/pdf/2401.12345v2"]
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(302, headers={"location": "http://127.0.0.1/private"})
    )) as client, pytest.raises(module.ImportProblem):
        module.fetch_arxiv("2401.12345", client=client)


def test_pdf_page_and_text_limits(monkeypatch):
    module = import_module("evidence_assistant.paper_import")
    writer = PdfWriter()
    for _ in range(module.MAX_PAGES + 1):
        writer.add_blank_page(width=100, height=100)
    output = BytesIO()
    writer.write(output)
    with pytest.raises(module.ImportProblem) as problem:
        module.extract_pdf(output.getvalue())
    assert problem.value.code == "pdf_too_long"
    monkeypatch.setattr(module, "MAX_TEXT_CHARS", 5)
    with pytest.raises(module.ImportProblem) as problem:
        module.extract_pdf(pdf_bytes())
    assert problem.value.code == "pdf_too_long"


def test_pdf_worker_deadline(monkeypatch):
    import subprocess
    module = import_module("evidence_assistant.paper_import")
    def stall(*args, **kwargs):
        raise subprocess.TimeoutExpired("parser", 30)
    monkeypatch.setattr(module.subprocess, "run", stall)
    with pytest.raises(module.ImportProblem) as problem:
        module.extract_pdf_isolated(pdf_bytes())
    assert problem.value.code == "pdf_timeout"


@pytest.mark.parametrize("mode", ["oversized_header", "oversized_stream", "html", "missing"])
def test_arxiv_rejects_bad_responses(mode, monkeypatch):
    module = import_module("evidence_assistant.paper_import")
    monkeypatch.setattr(module, "MAX_PDF_BYTES", 10)
    replies = {
        "oversized_header": httpx.Response(200, content=b"%PDF-x",
                                            headers={"content-length": "100"}),
        "oversized_stream": httpx.Response(200, content=b"%PDF-" + b"x" * 20),
        "html": httpx.Response(200, text="<html>Not a PDF</html>"),
        "missing": httpx.Response(404),
    }
    with httpx.Client(transport=httpx.MockTransport(lambda request: replies[mode])) as client:
        with pytest.raises(module.ImportProblem):
            module.fetch_arxiv("2401.12345", client=client)
