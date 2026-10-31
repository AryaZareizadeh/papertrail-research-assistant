# Add papers to your collection

Open **Add a paper** above the paper selector.

1. Choose **Upload PDF**, select a PDF, and click **Preview PDF**; or choose
   **arXiv link**, paste an `https://arxiv.org/abs/...` or `/pdf/...` link (an ID
   such as `2401.12345v2` also works), and click **Preview arXiv paper**.
2. Check that the extracted text is readable and edit **Paper title** if needed.
3. Click **Add to collection**. The app indexes the paper locally and selects it.
4. Ask a question and click a citation to inspect the extracted page text.

Imports require a prepared, ready API with the existing local embedding model.
Preview and save do not call the hosted answer model. Asking a question sends the
question and retrieved passages to the configured hosted provider, as before.

## Limits and source fidelity

- Maximum PDF size: 20 MiB; maximum 100 pages and 1 million extracted characters.
- Selectable text is required. Password-protected PDFs are rejected. OCR is not
  included; pages with no text are omitted, and entirely scanned PDFs are rejected.
- PDF extraction can scramble columns, equations, ligatures and tables. Review the
  preview before saving. The preview is limited to the first 20,000 characters;
  saved source text retains the full extraction within the limits above.
- Sources are labeled by PDF page. Character offsets refer to immutable extracted
  page text, not PDF glyph positions. This is text extraction, not figure/table reasoning.
- arXiv downloads can be blocked or throttled. Upload the PDF if import fails.
  Fetches use fixed HTTPS arXiv hosts, validate redirects and stop at the byte limit.
- The same PDF bytes reuse one paper, even if uploaded again under another filename.
  A revised or differently encoded PDF is a separate paper. Re-importing does not
  rename the existing entry. Metadata titles can be wrong; edit the preview title.

## Storage and deployment

Authorship identity questions prioritize the first-page author block. For known
small-cap extraction artifacts, the model receives a readable rendering alongside
the original cited text; stored source spans remain unchanged. First-listed and
corresponding author roles are distinct from an inferred "main contribution."
General questions about authors' methods keep normal retrieval. This also applies
to papers already imported; no re-upload is required.

The base QASPER corpus, indices, split manifests, and held-out results are unchanged.
Each saved paper gets a separate content-addressed directory with its original PDF,
source provenance, SQLite source/chunks and dense vectors. No benchmark references
are added. Imported papers are marked `user`, outside the official benchmark splits.

Local storage defaults to `library/` beside the configured artifact directory; set
`library_dir` in YAML to override it. Use a separate directory from datasets,
artifacts and reports. The default is ignored by Git. Protect this directory if the
papers are private. Preview files are bounded to ten PDFs and expire after 24 hours;
expired previews must be prepared again. Saving is atomic: indexing failure leaves
the paper out of the collection, and the preview can be retried.

Docker mounts a persistent `library` volume at `/library` owned by the application
user, separately from the read-only `/artifacts` bundle and `/runlogs` volume.
Ordinary restarts preserve papers. `docker compose down -v` deletes Docker volumes,
including the collection. Back up volumes before moving or resetting the app.

This is a single-process, local collection. Authentication, shared deployments,
editing/deleting papers and automatic version merging are outside this feature.

## HTTP endpoints

- `POST /imports/pdf?filename=paper.pdf`: raw PDF bytes, `Content-Type: application/pdf`.
- `POST /imports/arxiv`: JSON `{"url":"https://arxiv.org/abs/2401.12345"}`.
- Both return a preview ID, content-based paper ID, editable suggested title,
  page counts, origin, warnings and extracted text preview.
- `POST /imports/{preview_id}/confirm`: JSON `{"title":"My paper"}`. Returns
  `paper` and `already_exists`. The paper appears immediately in `GET /papers`.
- Existing `/questions` and paragraph routes work with the returned paper ID.

Input/extraction problems use 422, oversized documents 413, missing/expired previews
404, arXiv fetch failures 502, and unavailable collection storage 503. Responses
use the existing safe error envelope and request IDs.
