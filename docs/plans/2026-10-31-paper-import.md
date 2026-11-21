# Paper import implementation plan

**Goal:** Add selectable-text PDF upload and arXiv link import to the local collection.

**Architecture:** Preview extracted text and an editable title before confirmation. Commit each PDF as an atomic, content-addressed bundle in a separate writable library, leaving the frozen benchmark corpus unchanged. Reuse the existing chunker, embedding encoder, retrieval index, generation service, and exact-span citation validator.

**Tech stack:** Existing FastAPI/Streamlit/SQLite stack, pypdf, httpx.

**Spec:** User requested adding papers, approved PDF upload and arXiv links. Both use preview then save; text PDFs only, no OCR. Imports persist after restart and appear immediately in the selector.

## Global constraints

- Existing corpus, held-out artifacts, keys, and user documentation changes must be preserved.
- No hosted answer-generation tests or new benchmark runs.
- Local-only app; import documents stay in an ignored library directory or Docker volume.
- Limits: 20 MiB PDF, 100 pages, 1 million extracted characters. Reject encrypted, malformed, empty/scanned PDFs with actionable errors.
- Fetch only validated arXiv identifiers through fixed HTTPS arxiv.org endpoints; validate every redirect and stream with a byte limit.
- Preserve page labels, exact extracted text, source PDF hash, and stable source offsets. Extraction is not a guarantee of faithful layout or table interpretation.

## Review focus

- Duplicate bytes must not create duplicate papers; failed indexing must not publish a partial paper.
- Malicious URLs/redirects, oversized streams, path-like filenames, and invalid preview IDs must not escape the library or fetch arbitrary hosts.
- Preview changes must clear stale state, and import reruns must not regenerate answers.
- New collections must survive restart and retain readable original paragraphs.
- Read-only Docker assets must remain read-only; the library requires its own persistent writable volume.

## Tasks

- [x] 1. `paper_import.py`, `tests/test_paper_import.py`: write failing PDF/arXiv boundary tests, implement extraction/limits/validated fetching, pass focused checks. Pin pypdf in project and lock.
- [x] 2. `library.py`, `tests/test_library.py`, `config.py`, `schemas.py`: write failing persistence/duplicate/rollback/provenance tests. Implement per-paper bundles and reuse loaded encoder and answer-service boundaries; pass focused checks.
- [x] 3. `api.py`, `ui_client.py`, `ui_import.py`, `ui.py`, import API/client/UI tests: prove preview -> confirm -> select -> citation source routing; reject bad uploads and clear stale previews. Implement and pass focused tests.
- [x] 4. Docker configuration, README/API/containers/import documentation: add separate library volume and ignored local storage. Run full offline suite, Ruff, whitespace checks, independent review; rebuild local containers and verify UI/API readiness and import behavior without hosted inference.

## Execution ledger

- Baseline: 150 passed, 2 opt-in hosted tests skipped; Ruff passed before implementation; no source modifications since.
- Ruling: implement in this existing feature checkout to retain prepared assets and the running local app; preserve existing uncommitted documentation and review files. Do not auto-commit unrelated work or publish.
- Ruling: no second format/approval question; the user's `both` authorizes the proposed PDF and arXiv import feature. Implement inline; use a fresh reviewer for the final diff.
- Steps 1–3: RED failures observed before implementation; full suite 186 passed, 2 hosted skipped. Ruff and whitespace checks pass; uv reports all 83 installed packages compatible.
- Independent review found a P2 inferred-library overlap; reproduced with three failing config cases and fixed. Reviewer independently confirmed the fix and no remaining important findings.
- Real arXiv download/extraction check: `1706.03762`, 2,215,244 bytes, 15 pages, 39,496 extracted characters. No hosted inference.
- Final runtime: both containers rebuilt and healthy; browser arXiv preview/edit/save/automatic selection passed; HTTP upload of the same PDF reused its entry; 86-paper collection persisted after restart; base corpus hash unchanged. Linux offline suite also 186 passed, 2 skipped. Final layout/20 MiB widget adjustment passed 5 focused UI checks. Details: `reports/paper_import_verification.md`.
