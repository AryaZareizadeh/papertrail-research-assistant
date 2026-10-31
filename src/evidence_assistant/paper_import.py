"""Bounded PDF extraction and fixed-origin arXiv downloads; no model calls."""

import hashlib
import re
import subprocess
import sys
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import httpx
from pydantic import Field

from evidence_assistant.data import text_hash
from evidence_assistant.schemas import Paragraph, Record

MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_PAGES = 100
MAX_TEXT_CHARS = 1_000_000
IMPORT_MESSAGES = {
    "invalid_pdf": "This file could not be read as a PDF. Try another PDF.",
    "pdf_too_large": "Choose a PDF smaller than 20 MiB.",
    "pdf_too_long": "Choose a PDF with at most 100 pages and 1 million text characters.",
    "encrypted_pdf": "Password-protected PDFs are not supported. Upload an unencrypted copy.",
    "no_pdf_text": "No readable text was found. Scanned PDFs need OCR before import.",
    "pdf_timeout": "PDF extraction took too long. Try a smaller or simpler PDF.",
    "invalid_arxiv": "Enter an arXiv paper link or ID, such as https://arxiv.org/abs/2401.12345.",
    "arxiv_unavailable": "arXiv could not supply this PDF. Check the link or upload the PDF.",
    "preview_not_found": "This preview expired or is unavailable. Preview the paper again.",
    "library_unavailable": "The collection could not save this paper. Try again later.",
    "invalid_title": "Enter a paper title between 1 and 300 characters.",
}


class ImportProblem(Exception):
    def __init__(self, code, status=422):
        super().__init__(IMPORT_MESSAGES[code])
        self.code, self.status = code, status


class ExtractedPaper(Record):
    paper_id: str
    pdf_sha256: str
    title: str = Field(min_length=1, max_length=300)
    pages: int
    paragraphs: list[Paragraph]
    origin: str = "PDF upload"


def extract_pdf(data: bytes, *, filename: str = "paper.pdf") -> ExtractedPaper:
    from pypdf import PdfReader

    if len(data) > MAX_PDF_BYTES:
        raise ImportProblem("pdf_too_large", 413)
    if not data.startswith(b"%PDF-"):
        raise ImportProblem("invalid_pdf")
    digest = hashlib.sha256(data).hexdigest()
    paper_id = "pdf-" + digest
    try:
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise ImportProblem("encrypted_pdf")
        pages = len(reader.pages)
        if pages > MAX_PAGES:
            raise ImportProblem("pdf_too_long")
        paragraphs, count = [], 0
        for number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            count += len(text)
            if count > MAX_TEXT_CHARS:
                raise ImportProblem("pdf_too_long")
            if not text.strip():
                continue
            # A PDF page is the immutable source unit, even when extraction loses layout.
            paragraphs.append(Paragraph(
                paragraph_id=f"{paper_id}:page{number:04d}", paper_id=paper_id,
                section_index=number - 1, section_name=f"Page {number}", paragraph_index=0,
                text=text, text_sha256=text_hash(text),
            ))
        if not paragraphs:
            raise ImportProblem("no_pdf_text")
        fallback = Path(filename.replace("\\", "/")).stem or "Untitled paper"
        title = str((reader.metadata.title if reader.metadata else None) or fallback).strip()
        return ExtractedPaper(paper_id=paper_id, pdf_sha256=digest,
                              title=(title or fallback)[:300], pages=pages, paragraphs=paragraphs)
    except ImportProblem:
        raise
    except Exception:
        raise ImportProblem("invalid_pdf") from None


def extract_pdf_isolated(data: bytes, *, filename: str = "paper.pdf") -> ExtractedPaper:
    """Run untrusted parsing away from the server, with a wall-clock deadline."""
    if len(data) > MAX_PDF_BYTES:
        raise ImportProblem("pdf_too_large", 413)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "evidence_assistant.paper_import", filename[:300]],
            input=data, capture_output=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired:
        raise ImportProblem("pdf_timeout") from None
    if result.returncode:
        code = result.stdout.decode("utf-8", errors="replace").strip()
        raise ImportProblem(code if code in IMPORT_MESSAGES else "invalid_pdf")
    try:
        return ExtractedPaper.model_validate_json(result.stdout)
    except ValueError:
        raise ImportProblem("invalid_pdf") from None


_ARXIV_ID = re.compile(r"(?:\d{4}\.\d{4,5}|[a-z][a-z.-]+(?:\.[A-Z]{2})?/\d{7})(?:v[1-9]\d*)?")


def arxiv_identifier(value: str) -> str:
    value = value.strip()
    if "://" in value:
        url = urlsplit(value)
        if (url.scheme != "https" or url.netloc not in {"arxiv.org", "www.arxiv.org"}
                or url.query or url.fragment):
            raise ImportProblem("invalid_arxiv")
        match = re.fullmatch(r"/(?:abs|pdf)/(.+)", url.path)
        value = match[1] if match else ""
    value = value.removesuffix(".pdf")
    if not _ARXIV_ID.fullmatch(value):
        raise ImportProblem("invalid_arxiv")
    return value


def fetch_arxiv(value: str, *, client=None) -> tuple[bytes, str]:
    identifier = arxiv_identifier(value)
    url = f"https://arxiv.org/pdf/{identifier}"
    context = nullcontext(client) if client else httpx.Client(
        timeout=httpx.Timeout(30, connect=10), follow_redirects=False, trust_env=False,
        headers={"User-Agent": "PaperTrail/0.1 (local single-paper import)"},
    )
    try:
        with context as connection:
            for _ in range(4):
                # Validate every hop; user input can never supply an arbitrary fetch URL.
                parsed = urlsplit(url)
                if (parsed.scheme != "https" or parsed.netloc not in {
                    "arxiv.org", "www.arxiv.org", "export.arxiv.org"
                } or not parsed.path.startswith("/pdf/") or parsed.query or parsed.fragment):
                    raise ImportProblem("arxiv_unavailable", 502)
                with connection.stream("GET", url, follow_redirects=False) as response:
                    if response.is_redirect:
                        url = urljoin(url, response.headers.get("location", ""))
                        continue
                    response.raise_for_status()
                    if int(response.headers.get("content-length", "0")) > MAX_PDF_BYTES:
                        raise ImportProblem("pdf_too_large", 413)
                    blocks, size = [], 0
                    for block in response.iter_bytes():
                        size += len(block)
                        if size > MAX_PDF_BYTES:
                            raise ImportProblem("pdf_too_large", 413)
                        blocks.append(block)
                    data = b"".join(blocks)
                    if not data.startswith(b"%PDF-"):
                        raise ImportProblem("arxiv_unavailable", 502)
                    return data, f"https://arxiv.org/abs/{identifier}"
    except (httpx.HTTPError, ValueError):
        raise ImportProblem("arxiv_unavailable", 502) from None
    raise ImportProblem("arxiv_unavailable", 502)


if __name__ == "__main__":
    # Unix memory cap supplements the cross-platform 30-second parent timeout.
    if sys.platform != "win32":
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (768 * 1024**2, 768 * 1024**2))
    try:
        extracted = extract_pdf(sys.stdin.buffer.read(MAX_PDF_BYTES + 1), filename=sys.argv[1])
        sys.stdout.buffer.write(extracted.model_dump_json().encode("utf-8"))
    except ImportProblem as problem:
        sys.stdout.write(problem.code)
        sys.exit(1)
