# PaperTrail Development Guide

This guide began as a development plan and now records implementation progress. Checkboxes track each task, and the verification reports and acceptance limits below document completion.

**Goal:** Build a research-paper assistant that answers questions about a selected paper, shows the source passages supporting its answer, and declines when it cannot find sufficient support.

**Architecture:** Convert QASPER papers into a document-only corpus, retain stable paragraph identifiers, and compare keyword, embedding, and hybrid retrieval. Supply retrieved passages to a language model and construct citations from stored source text. A separate evaluator measures answers, evidence retrieval, citation support, and abstention without exposing benchmark annotations to the application.

**Tech Stack:** Python, SQLite, NumPy, rank-bm25, sentence-transformers, one configurable language-model backend, FastAPI, Streamlit, pytest, and Docker. The user selected a free hosted API: start with Groq's Free Plan and `openai/gpt-oss-20b`, subject to a live account/model smoke test. The core retrieval pipeline runs independently of generation.

**Spec:** The design contract in Section 2 of this document. The defaults below are proposed implementation choices, not requirements previously supplied by Arya.

**Prepared:** 26 October 2026. **Updated:** 31 October 2026.
**Deliverable type:** Development guide and implementation checklist for the local application.

**Current status:** The local application is ready to try. Tasks 1–10 are
implemented and closed for the local milestone with the accepted exceptions below.
All 80 checklist items are closed, including public source publication. An item that
records a waiver or deferral does not mean its original acceptance check ran.

- Groq GPT-OSS-20B plus dense retrieval, the shared FastAPI pipeline, Streamlit
  evidence viewer, recorded offline demo, and CPU Docker packaging are integrated.
- Current verification: 195 deterministic tests passed, two hosted tests skipped,
  Ruff passed, and both local services are ready. PDF/arXiv imports and authorship
  context handling are implemented; the original 85-paper corpus remains separate
  from the persistent user collection. Earlier asset-integrity checks remain in
  the dated readiness audit; new feature checks are in the import/authorship reports.
- The held-out pilot is complete: 187/187 attempted, 185 completed responses,
  2 retained rate-limit failures, and zero unattempted cases. The user authorized
  the final 33 cases; all original 154 records and the frozen candidate are intact.
  Whole-pilot Answer F1 is 0.2600; see `reports/evaluation.md` for denominators.
- The user accepted the labeled 30-response agent audit. Human claim-support
  review and peer usability feedback remain unavailable/deferred. Live API
  generation remains unrun under the user's instruction to stop model tests.
- Source is published at [AryaZareizadeh/papertrail-research-assistant](https://github.com/AryaZareizadeh/papertrail-research-assistant)
  on `main`, following the user's explicit public-publication request. GitHub
  Actions status is separate from local checks. The app remains locally hosted.

See [the current readiness audit](reports/readiness_audit.md),
[local release verification](reports/release.md), and
[the experiment log](reports/experiment_log.md) for evidence and limits.

## 1. How to use this guide

Work through the tasks in order. Finish each task's acceptance checks before adding the next feature. Keep a short experiment log explaining what changed, why, and what the measurements showed.

The commands using `evidence_assistant.cli` refer to this repository's implemented
package. The task instructions below retain the build sequence and initial design
choices; use the README for current setup and launch commands. Calibration and
hosted evaluation commands make model requests and are not part of a read-only
readiness check. Preserve the completed held-out run and its consumed-selection marker.

Your first useful milestone is a reliable evidence retriever. The next is an evaluated answer pipeline. The interface and packaging come after those foundations.

### What this project adds to your portfolio

You already have Python, PyTorch, model evaluation, scientific research, FastAPI, and Docker experience in your résumé. This project adds a concrete demonstration of document retrieval, embeddings, LLM integration, source attribution, systematic evaluation, and application delivery.

Its main contribution is applied NLP/LLM engineering. Your imaging work remains the evidence for developing and training deep-learning models. A small, carefully measured system will make a stronger portfolio artifact than an unfinished collection of frameworks.

### Planning estimate

As a rough planning allowance, reserve 40–70 focused hours for a modest first version, plus learning time. Hardware, model access, and data-cleaning problems can change that substantially. Use the milestones, rather than a calendar deadline, to decide whether the work is complete.

## 2. Project scope and design contract

### 2.1 The user and the problem

The first user is a researcher reading an unfamiliar ML/NLP paper. They select a paper and ask questions such as:

- Which datasets and evaluation metrics did the authors use?
- What comparison supports the authors' main claim?
- Does the paper describe the requested experiment or limitation?

The assistant gives a short answer with clickable source passages. The user can read the evidence and decide whether the interpretation is justified.

### 2.2 First-version boundaries

| Decision | Version 1 scope |
| --- | --- |
| Documents | QASPER papers plus selectable-text PDF uploads and arXiv imports (31 October extension) |
| Question scope | One explicitly selected paper per question |
| Input | Released structured paper text |
| Citations | Paper, section, paragraph, and exact source span |
| Supported evidence | Text paragraphs |
| Interface | Paper selector, question input, answer, and evidence viewer |
| Execution | Local development and a reproducible container |
| Model training | No fine-tuning required for the initial version |

Selectable-text PDF ingestion and arXiv imports were added on 31 October 2026;
see [paper imports](docs/paper_import.md). OCR, visual table/figure reasoning,
Persian support, cross-paper comparisons, authentication and public multi-user
hosting remain later extensions. Imported documents use actual PDF page labels
and offsets into extracted text, without glyph/region coordinates. QASPER's
paragraph annotations do not supply PDF page coordinates. Existing evaluation
results do not measure quality on new user documents.

Start with five training papers for debugging. Use a deterministic pilot of 30 validation papers and 50 test papers for the first evaluation. Retain every question from the selected papers. Record that these are pilot subsets, not full-benchmark results. Expand to the full official splits after the pipeline is stable.

### 2.3 What a successful answer looks like

Each substantive claim must point to one or more retrieved source chunks. Clicking a citation must open the corresponding section and source paragraph with the cited span highlighted.

If the system lacks sufficient evidence, display:

> I couldn't find sufficient supporting evidence in this paper.

This means the system did not establish an answer. It does not prove that the complete paper lacks one: retrieval can fail.

Attaching an existing quote establishes traceability, not semantic correctness. Measure whether the quoted material actually supports the answer separately.

### 2.4 Initial technical choices

- **Python:** Use a version supported by the chosen packages; Python 3.11 or newer is the proposed floor. Record the actual version and lock working dependency versions after installation.
- **Storage roadmap:** Start version 1 with SQLite for paper metadata, source paragraphs, chunks, and run records. After the first version is complete, migrate storage to PostgreSQL in a later version. Use SQL parameter binding and stable keys, and keep database access in `store.py` so the migration can preserve the retrieval, generation, and API contracts.
- **Keyword retrieval:** BM25 through `rank-bm25`.
- **Dense retrieval:** `sentence-transformers/all-MiniLM-L6-v2` and NumPy cosine similarity. Its published embedding dimension is 384 and its default input truncation limit is 256 wordpieces; respect the tokenizer limit when chunking. [Model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Hybrid retrieval:** Reciprocal rank fusion of BM25 and dense rankings, with a fixed fusion constant of 60 and one-based ranks.
- **Generation:** One model through a small adapter. Use the same model, prompt version, and generation settings across retrieval comparisons.
- **Interface:** Streamlit calls the FastAPI service over HTTP. It does not implement its own retrieval path.
- **Initial context policy:** Return up to five chunks per question, with a proposed cap of 1,536 evidence tokens measured by the generation model's tokenizer. Start with a 4,096-token model context, reserve 512 output tokens and a 256-token safety margin, and count instructions/question/metadata as well. Confirm that the chosen model supports this context before using these defaults. Keep the policy fixed across compared methods and record actual context lengths.

Choose the generation model after a small hardware/access smoke test. Put its exact identifier and revision or local model digest in configuration. Do not claim a GPU-memory requirement, model quality level, or runtime before measuring your setup. Retrieval work can proceed while that choice is being resolved.

### 2.5 Definition of done

Version 1 is complete when:

- A fresh environment can reproduce ingestion, indexing, evaluation, and the demo using documented commands.
- Runtime retrieval contains paper text and metadata only; benchmark answers and evidence annotations are isolated.
- All retrieval methods search the selected paper and use the same evaluation questions and context policy.
- Citations resolve to immutable source spans and pass mechanical validation.
- The evaluation includes supported answers, unanswerable questions, unnecessary refusals, and system errors.
- The report includes baselines, measured results, uncertainty about those results, failure examples, latency, and resource usage.
- The repository contains a runnable demo and an honest account of what you personally implemented.

No particular accuracy percentage is promised. A well-explained negative result is valid evidence of engineering work.

## 3. Global constraints

- Keep the official train, validation, and test paper assignments. Assert that paper IDs do not overlap.
- Use training annotations for development or later supervised training; use validation for configuration choices; freeze those choices before final test evaluation.
- The model may read the selected test paper at inference time. Test answer/evidence labels may not enter the index, prompt, tuning loop, or application cache.
- Preserve each annotator's answer and evidence as a separate reference. Do not merge every reference into one mandatory evidence set.
- Keep original paragraph text unchanged. Store matching-normalized text separately.
- Never show a generated quotation or page number as if it came from the source. Construct displayed quotations from stored source offsets.
- Apply paper filtering before ranking and before any reranking stage.
- Use the same dataset manifest, chunking version, model versions, and evidence budget for a claimed method comparison.
- Save question-level predictions and errors. Failed calls remain in the evaluation denominator.
- Keep raw data, model weights, keys, and local databases out of Git. Publish download instructions, provenance, and results instead.
- Treat document text as evidence to analyze. It cannot change the application's instructions, authorize actions, or execute tools.
- Any thresholds or target values introduced below are initial design settings, not validated performance claims.

## 4. Review focus

These five failure classes need explicit tests in the task that owns them:

1. **Gold-label leakage:** A secret string placed only in a benchmark answer must never appear in runtime documents or prompts. Task 2 owns this.
2. **Wrong-paper retrieval:** A very similar paragraph from another paper must not enter the selected paper's results. Task 4 owns this.
3. **Broken or misleading citations:** A fabricated ID, altered quote, or stale source span must fail validation. Task 5 owns this.
4. **False certainty and over-refusal:** The evaluator must distinguish gold unanswerability, retrieval failure, inappropriate refusal, and provider errors. Task 6 owns this.
5. **Truncation and text-only limitations:** Long paragraphs, repeated passages, missing evidence mappings, and figure/table-dependent questions must be handled and reported explicitly. Tasks 3 and 6 own this.

## 5. Repository structure

Create the following structure gradually as the tasks require it:

```text
papertrail-research-assistant/
  README.md
  pyproject.toml
  requirements.lock.txt
  .gitignore
  .env.example
  config.yaml
  Dockerfile
  compose.yaml
  src/evidence_assistant/
    __init__.py
    config.py          # Load and validate configuration.
    schemas.py         # Shared typed records and API contracts.
    cli.py             # Commands described in this guide.
    data.py            # Downloads, manifests, normalization, split isolation.
    chunking.py        # Token-bounded chunks and source offsets.
    store.py           # SQLite persistence and source lookup.
    retrieval.py       # BM25, dense, and hybrid retrieval.
    generation.py      # Model adapter, prompts, draft validation.
    service.py         # Retrieve, generate, validate, and assemble an answer.
    evaluation.py      # Offline reference mapping and scoring.
    api.py             # FastAPI endpoints.
    ui.py              # Streamlit client.
  tests/
    fixtures/          # Tiny synthetic examples; no model download needed.
    test_config.py
    test_data.py
    test_chunking.py
    test_store.py
    test_retrieval.py
    test_generation.py
    test_evaluation.py
    test_api.py
  data/
    raw/               # Immutable downloaded archives and source JSON.
    corpus/            # Runtime paper/paragraph records only.
    evaluation/        # Questions, answers, references, eligibility metadata.
    manifests/         # Split selections, hashes, counts, source revisions.
  artifacts/
    corpus.sqlite
    embeddings.npy
    index_manifest.json
  reports/
    experiment_log.md
    evaluation.md
    failure_analysis.md
    runs/              # Per-question predictions and aggregate metrics.
  docs/
    architecture.md
    data_card.md
    model_card.md
  .github/workflows/tests.yml
```

The corpus and evaluation directories have different consumers. The application receives the corpus and index artifacts. Only the offline evaluator reads `data/evaluation/`.

## 6. Shared data and interface contracts

Define these records in `schemas.py` before implementing modules that exchange them. Use dataclasses or Pydantic models consistently.

| Record | Required fields |
| --- | --- |
| `Paper` | `paper_id`, `split`, `title`, `abstract`, `source_revision` |
| `Paragraph` | `paragraph_id`, `paper_id`, `section_index`, `section_name`, `paragraph_index`, `text`, `text_sha256` |
| `Chunk` | `chunk_id`, `paragraph_id`, `paper_id`, `section_name`, `start_char`, `end_char`, `text`, `token_count`, `chunking_version` |
| `RetrievedChunk` | `chunk`, `rank`, `score`, `method` |
| `AnswerReference` | `annotation_id`, `answer_type`, `answer_text`, `unanswerable`, `evidence: list[str]`, `highlighted_evidence: list[str]`; retain the raw answer fields needed by the official evaluator |
| `GoldQuestion` | `question_id`, `paper_id`, `question`, `references`, `annotation_disagreement`, `evidence_mapping_status`, `uses_float_evidence` |
| `DraftClaim` | `text`, `citation_chunk_ids` |
| `DraftAnswer` | `status`, `claims`; status is `answered` or `insufficient_evidence` |
| `Citation` | `chunk_id`, `paper_id`, `paragraph_id`, `section_name`, `start_char`, `end_char`, `quote` |
| `AnswerResult` | `request_id`, `paper_id`, `status`, `claims`, `citations`, `retrieved_chunk_ids`, `method`, `model_id`, `prompt_version`, `index_version`, `latency_ms` |
| `AppConfig` | Resolved data/artifact/report paths; seed; retrieval/chunking settings; embedding model/revision; generation model/digest, endpoint, tokenizer, context/output/evidence limits; prompt version and timeout |
| `DataManifest` | Dataset version, source URLs, archive/file hashes, observed split counts, selection seed/rule, selected paper IDs, normalization version |
| `IndexManifest` | Corpus/chunking hashes, embedding model/revision, tokenizer settings, vector dimension, ordered chunk IDs, artifact hashes, index version |
| `EvidenceMapping` | Question ID and separate annotation records; each evidence item retains its original string, candidate paragraph IDs, match method, and status (`exact`, `whitespace`, `float`, or `unmapped`) |
| `RetrievalMetrics` / `AnswerMetrics` | Metric values plus per-metric numerators, denominators, excluded counts/reasons, split/slice, run ID, and policy/configuration hashes |

Use deterministic IDs such as `paper_id:s0002:p0004` and `paper_id:s0002:p0004:c0001`. A chunk belongs to exactly one source paragraph in version 1.

Character offsets use Python string indexing and half-open ranges `[start_char:end_char]` within the original paragraph. They are not byte offsets. Define `GoldQuestion.references` as `list[AnswerReference]`. Store each evidence item separately: if identical text appears at multiple positions, its candidate IDs are alternative matches for that one item, not additional required evidence items.

For `insufficient_evidence`, return no factual claims and no purported answer citations. Keep retrieval diagnostics in the run record. For an answered response, every claim needs at least one valid citation.

The API derives display text from the validated claims. It should not maintain a second, independently generated answer that could disagree with them.

## 7. Development tasks

For each task: write the specified failing test, confirm the failure comes from the missing behavior, implement the smallest complete behavior, run the checks, inspect the output, and commit the working change locally. Integration tests that contact a real model must be explicitly enabled; ordinary tests use deterministic fake responses.

### Task 1 — Establish a runnable project and configuration

**Create:** `pyproject.toml`, `.gitignore`, `.env.example`, `config.yaml`, `config.py`, `schemas.py`, `cli.py`, and `tests/test_config.py`.

**Interfaces:** `load_config(path: Path) -> AppConfig`. CLI entry: `python -m evidence_assistant.cli`.

- [x] Create a new project folder in your preferred development location and initialize Git.
- [x] Create a virtual environment. In PowerShell:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If script activation is restricted, invoke `.\.venv\Scripts\python.exe` directly instead of changing system execution policy.

- [x] In `pyproject.toml`, declare a `src/` package using setuptools, the supported Python floor, runtime dependencies, and a development extra. Start with `numpy`, `rank-bm25`, `sentence-transformers`, `fastapi`, `uvicorn`, `httpx`, `pydantic`, `pyyaml`, and `streamlit`; use `pytest` and `ruff` for development. Avoid adding an orchestration framework before you have a need for it.
- [x] Install with `python -m pip install -e ".[dev]"`. After a clean install works, record exact resolved versions in `requirements.lock.txt` and verify installation from that lock in a second environment.
- [x] Add a test that rejects `top_k=0`, an unknown retrieval method, and overlapping data directories. It must accept valid default configuration.
- [x] Implement configuration with these initial settings: `seed=42`, `top_k=5`, `candidate_k=20`, `rrf_k=60`, `chunk_tokens=192`, `chunk_overlap_tokens=32`, `generator_context_tokens=4096`, `max_evidence_tokens=1536`, `max_output_tokens=512`, and `context_safety_margin_tokens=256`. Validate the configured model/tokenizer combination; embedding and generation token counts are different measurements.
- [x] Add `python -m evidence_assistant.cli doctor`. It prints Python/package versions, configured paths, selected model identifiers, and whether required artifacts exist. Missing artifacts are reported clearly without downloading them automatically.
- [x] Add ignore rules for `.venv/`, `.env`, downloaded data, model caches, databases, large embeddings, and local run outputs. Commit a sanitized `.env.example` and retain small aggregate reports explicitly.

**Check:** `python -m pytest tests/test_config.py -q` passes; the CLI help and doctor command work. Keep this first commit runnable even though no documents have been indexed yet.

### Task 2 — Download and normalize QASPER without leaking annotations

**Create:** `data.py`, the data manifest format, and `tests/test_data.py`.

**Interfaces:**

```python
download_qasper(destination: Path) -> DataManifest
normalize_release(raw_dir: Path, corpus_dir: Path, evaluation_dir: Path) -> DataManifest
select_papers(paper_ids: list[str], split: str, limit: int, seed: int) -> list[str]
```

Use the original v0.3 JSON archives as the canonical format. The official loader identifies these sources:

- [Training and development archive](https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz)
- [Test and evaluator archive](https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz)
- Expected files: `qasper-train-v0.3.json`, `qasper-dev-v0.3.json`, and `qasper-test-v0.3.json`.

Verify download status, inspect archive members, and compute SHA-256 hashes. Extract only the expected files into the project's data directory. These URLs and version names are documented in the [official dataset loader](https://huggingface.co/datasets/allenai/qasper/raw/main/qasper.py).

- [x] Write a synthetic fixture matching the original release: a dictionary keyed by paper ID, with lists of sections, paragraphs, questions, and answer annotations. Do not mix this with Hugging Face's possible dictionary-of-lists representation.
- [x] Add `test_normalizer_separates_runtime_and_gold`. Put a distinctive secret string only in a fixture's gold answer; assert it is absent from exported paper text and runtime metadata. Reuse this fixture to test chunks in Task 3 and model prompts in Task 5.
- [x] Normalize the release into document-only records in `data/corpus/` and question/reference records in `data/evaluation/`. Runtime documents may contain the paper's natural text, including prose that happens to answer a question; they must not contain the separate QA annotations.
- [x] Make the abstract citable too. If it is not already present as a full-text paragraph, store it under a reserved `Abstract` section with `section_index=-1` and an ID such as `paper_id:abstract:p0000`. Preserve the original full-text section positions.
- [x] Preserve every answer annotation, its answer type, evidence strings, and highlighted evidence. An empty evidence list does not automatically mean a question is unanswerable.
- [x] Check paper-level split disjointness and count actual papers, questions, and annotations. The official release metadata lists 888 training, 281 validation, and 416 test papers. Record observed counts and investigate discrepancies rather than silently discarding rows. [Official split metadata](https://huggingface.co/datasets/allenai/qasper/blob/main/dataset_infos.json)
- [x] Select the debug/validation/test pilot papers by sorting a SHA-256 hash of `seed + split + paper_id` and taking the requested count. Save the IDs before inspecting performance. Do not choose papers based on how well a model answers them.
- [x] Retain all questions from those selected papers. Save dataset URLs, version, hashes, counts, selected IDs, and the selection rule in `data/manifests/`.
- [x] Read several training examples manually to understand the problem. Leave test answers out of the development workflow.

**Commands after implementation:**

```powershell
python -m evidence_assistant.cli download --config config.yaml
python -m evidence_assistant.cli normalize --config config.yaml
python -m pytest tests/test_data.py -q
```

**Check:** No split overlap; corpus/gold separation passes; every selected question points to an existing paper; source counts and hashes are saved. A dataset row represents a paper, not necessarily one question.

### Task 3 — Preserve source provenance and create bounded chunks

**Create:** `chunking.py`, `store.py`, `tests/test_chunking.py`, and `tests/test_store.py`.

**Interfaces:**

```python
chunk_paragraph(paragraph: Paragraph, tokenizer, config: AppConfig) -> list[Chunk]
build_store(papers: list[Paper], paragraphs: list[Paragraph], chunks: list[Chunk], db_path: Path) -> None
get_chunk(db_path: Path, chunk_id: str) -> Chunk | None
```

- [x] Test a short paragraph, an empty paragraph, Unicode text, repeated identical paragraphs, and a paragraph longer than the embedding model's limit.
- [x] Store original text unchanged. Give repeated paragraphs different positional IDs even when their hashes match.
- [x] Split long paragraphs into overlapping token windows. Preserve `start_char`/`end_char` using tokenizer offsets; assert `paragraph.text[start_char:end_char] == chunk.text` for every chunk. Avoid trying to reconstruct character offsets by decoding tokens.
- [x] Target 192 content tokens with 32-token overlap. If a section/title prefix is embedded, cap that prefix and verify the combined input, including special tokens, fits the model's actual maximum. Do not allow silent tokenizer truncation.
- [x] Create SQLite tables for `papers`, `paragraphs`, and `chunks` with primary keys, foreign keys, split metadata, and source hashes. Add run-record tables when the answer service needs them.
- [x] Save a chunking manifest with configuration and version. A changed chunking policy requires rebuilding embeddings and invalidating incompatible caches.
- [x] Export paragraph statistics: counts, lengths, empty records, duplicate-text occurrences, and overlong paragraphs split. Keep malformed rows visible in a rejection log.

**Commands:**

```powershell
python -m evidence_assistant.cli chunk --config config.yaml
python -m pytest tests/test_chunking.py tests/test_store.py -q
```

**Check:** Every citation candidate has an exact source location; no text disappears through truncation; repeated passages remain distinguishable.

### Task 4 — Build retrieval baselines before adding answer generation

**Create:** `retrieval.py` and `tests/test_retrieval.py`.

**Interfaces:**

```python
build_index(db_path: Path, output_dir: Path, config: AppConfig) -> IndexManifest
retrieve(question: str, paper_id: str, method: str, top_k: int, index) -> list[RetrievedChunk]
```

- [x] Create a fixture with two papers containing similar terms. Assert that requesting one paper never returns the other's chunks, including through the hybrid path.
- [x] Implement BM25 with a documented English tokenizer. For example, case-fold and extract word/number tokens; keep the same tokenizer for queries and documents.
- [x] Encode chunks with the configured sentence-transformer. Cache normalized vectors and their ordered chunk IDs. For normalized vectors, compute cosine rankings with a dot product.
- [x] Verify vector row count, chunk-ID order, dimension, and model revision against the index manifest. Reject incompatible artifacts.
- [x] Implement hybrid retrieval using `sum(1 / (60 + rank))` across the two candidate lists, where ranks start at 1. Use up to 20 candidates per method, deduplicate by chunk ID, and return the top five. Use deterministic tie-breaking by chunk ID.
- [x] Apply paper filtering before scoring/ranking. Return an empty list for a paper with no indexable text and a distinct unknown-paper error for an invalid ID.
- [x] Add CLI output showing chunk IDs, section labels, scores, and source text. Inspect at least ten training questions and explain why each result is relevant or irrelevant.
- [x] Measure index-build time and retrieval latency separately. Keep model download/load time separate from warm-query timing.

**Commands:**

```powershell
python -m evidence_assistant.cli index --config config.yaml
python -m evidence_assistant.cli retrieve --paper-id PAPER_ID --question "Which datasets were used?" --method bm25
python -m evidence_assistant.cli retrieve --paper-id PAPER_ID --question "Which datasets were used?" --method dense
python -m pytest tests/test_retrieval.py -q
```

Replace `PAPER_ID` with an actual debug-paper ID. Add a cross-encoder reranker only as a later measured experiment, after these baselines work.

**Check:** You can explain a retrieval result without using an LLM. All methods respect paper boundaries and load only compatible artifacts.

### Task 5 — Generate concise answers and construct valid citations

**Create:** `generation.py`, `service.py`, and `tests/test_generation.py`.

**Interfaces:**

```python
GroqAdapter.generate(messages: list[dict], schema: dict) -> ProviderReply
parse_draft(content: str) -> DraftAnswer
validate_draft(draft: DraftAnswer, retrieved: list[RetrievedChunk]) -> None
answer_question(question: str, paper_id: str, method: str, service) -> AnswerResult
```

- [x] Use a fake model response to test valid claims, a fabricated citation ID, a citation from another paper, answered output with no claims, invalid JSON, a model timeout, and evidence that exceeds the context budget. These tests must not contact a provider.
- [x] Implement one hosted generation adapter. For Groq, use `/openai/v1/chat/completions`, request strict JSON schema, and disable streaming. Configure a fixed model identifier, temperature 0, low reasoning effort, and an output limit. Record runtime settings; temperature 0 is not a guarantee of identical outputs across hardware or versions. Read `GROQ_API_KEY` from the ignored `.env` or environment. Keep the account on the Free Plan; do not add paid fallbacks. [Groq API](https://console.groq.com/docs/openai), [structured outputs](https://console.groq.com/docs/structured-outputs)
- [x] Supply only the question, selected-paper metadata, and retrieved text chunks with allowed citation IDs. Never pass gold answers, evidence annotations, or dataset question metadata beyond the question text itself.
- [x] Instruct the model to make only source-supported claims and to use `insufficient_evidence` when it cannot justify an answer. Keep this as a versioned prompt file or constant.
- [x] Validate that every cited ID belongs to the retrieved chunks for this paper. Build each displayed quote from the stored chunk/source offsets, not model-authored quotation text.
- [x] For answered output, require at least one claim and at least one citation per claim. For insufficient evidence, require empty claims. Resolve duplicate citations deterministically.
- [x] Return a distinct model/service error when generation times out or produces invalid structured output. Do not count these failures as successful abstentions. Allow at most one bounded retry for a transient transport failure; log both attempts.
- [x] Enforce the generator-specific context budget using a pinned matching tokenizer and chat template. Reserve space for instructions, question, metadata, output, and the safety margin. If evidence must be reduced, drop the lowest-ranked chunks, record which chunks were actually supplied, and keep the same policy across methods. Do not silently cut quoted source text. If the chosen backend's token counting cannot be verified, document that limitation and resolve it before making fixed-token-budget comparisons.
- [x] Add a fixture paragraph containing an instruction to ignore the question. Verify that the prompt treats it as quoted document content and that the application exposes no execution tools.
- [x] Store run ID, selected paper, question, retrieved/supplied chunk IDs, source/index/model/prompt versions, status, latency, and errors. Keep actual and estimated token counts distinguishable.

**Command:**

```powershell
python -m evidence_assistant.cli answer --paper-id PAPER_ID --question "Which datasets were used?" --method hybrid
python -m pytest tests/test_generation.py -q
```

**Check:** Citations are mechanically traceable. A manual review still checks whether the source supports the interpretation. Never label an answer “verified” solely because its citation IDs exist.

### Task 6 — Build the evaluation that makes this a credible project

**Create:** `evaluation.py`, `tests/test_evaluation.py`, and the first evaluation report.

**Interfaces:**

```python
map_evidence(question: GoldQuestion, paragraphs: list[Paragraph]) -> EvidenceMapping
evaluate_retrieval(predictions, references, policy) -> RetrievalMetrics
evaluate_answers(predictions, references, policy) -> AnswerMetrics
```

- [x] Test perfect evidence retrieval, partial evidence, wrong evidence, no evidence, duplicate chunks from one paragraph, multiple annotators, missing predictions, and a provider error.
- [x] Map full evidence paragraphs to source paragraph IDs using exact matching first. Permit documented whitespace-only normalization as a fallback. Preserve all positional matches when text repeats and record the ambiguity. Do not use fuzzy guessing to manufacture a gold location.
- [x] Keep `highlighted_evidence` separate from paragraph-level `evidence`. Log unmatched references and evidence markers beginning `FLOAT SELECTED` as their own categories.
- [x] Preserve reference answer/evidence pairs per annotator. Score against individual reference sets; do not create an artificial union of all evidence.
- [x] Tag answerability disagreement. For product abstention metrics, use consensus-answerable and consensus-unanswerable slices and report mixed annotations separately. Do not infer answerability from whether evidence is empty.
- [x] Freeze a text-only question policy before test evaluation: exclude a question from the strict text-only slice if any retained annotation uses figure/table evidence. Also flag unmapped evidence and absence-based answers without positive text evidence. Publish counts and reasons by split; never relabel these questions unanswerable.
- [x] Keep predictions for all selected questions and report whole-selected-set results as well as the declared text-only slice. This prevents favorable filtering from hiding difficult cases.
- [x] Evaluate BM25, dense, and hybrid retrieval on exactly the same questions, with the same top-k and evidence-token cap.
- [x] Run generation with each retrieval method using the same model and prompt. First run a small validation subset to measure runtime before starting a large batch.
- [x] Save per-question results with a run manifest and generate the metrics below. Review at least 30 validation answers manually across correct answers, incorrect answers, refusals, and difficult evidence cases. The user accepted the explicitly labeled agent audit for this milestone; do not present it as human review.
- [x] Implement and verify freezing of dataset selection, eligibility policy, prompt, retrieval parameters, model artifacts, and scoring rules. Freeze the baseline for Task 7 comparisons. Finish final configuration choices on validation in Task 7, then freeze the final candidate before the pilot test.

#### Required metrics and their denominators

| Metric | Definition and interpretation |
| --- | --- |
| Evidence Hit@5 | Fraction of eligible answerable questions for which the supplied top-five chunks cover at least one valid gold evidence paragraph. |
| Evidence Recall@5 | For each eligible question, the fraction of paragraphs in a reference evidence set covered by supplied chunks; use the best matching annotator reference. Report the mean and denominator. |
| Complete-evidence coverage | Fraction of eligible questions for which one annotator's complete evidence set is covered. Finding one paragraph may not be enough. |
| Answer F1 | Use the official QASPER evaluator for benchmark-compatible scoring, with the evaluated question IDs and any filtering declared. |
| Citation validity | Fraction of emitted citation records that resolve to an allowed source span. This is a structural check. |
| Claim support | Fraction of answered claims supported by their cited passages; mark fully supported, partially supported, or unsupported. Publish the rubric, sample, and reviewer identity. The user accepted an agent audit for the baseline; label it accordingly and leave human-audited support unavailable until a human review occurs. |
| Abstention precision | Of deliberate insufficient-evidence responses on consensus-labeled questions, how many are gold-unanswerable? A retrieval miss on an answerable question is not a correct refusal. |
| Unanswerable recall | Of consensus-unanswerable questions, how many receive a deliberate insufficient-evidence response? |
| False-refusal rate | Fraction of consensus-answerable questions refused. Report this alongside answer coverage so refusing everything cannot appear successful. |
| System-error rate | Fraction of all requested cases that fail through timeout, invalid output, or service errors. |
| Latency/resources | Warm end-to-end p50/p95 latency, cold startup time separately, model identifier, hardware, memory observations, and measured or explicitly estimated token/cost usage. |

Collapse retrieved chunks to paragraph IDs for paragraph metrics; multiple chunks from the same paragraph do not earn repeated credit. Evaluate the chunks actually sent to generation, not an earlier ranking before budget trimming. For repeated text, a match to an equivalent positional occurrence can satisfy one evidence item; do not require every duplicate occurrence. A paragraph hit is a coarse retrieval measurement: a chunk may cover only part of that paragraph, so the metric does not establish that all supporting text reached the model. The claim-support audit checks that separately.

Exclude empty gold evidence sets from retrieval-recall denominators and show how many were excluded. Annotated evidence is not necessarily the only valid support in a paper; review disagreement cases rather than treating every different citation as a hallucination.

The [official evaluator](https://raw.githubusercontent.com/allenai/qasper-led-baseline/main/scripts/evaluator.py) scores against multiple references and assigns zero to missing predictions. Its text-evidence option removes figure/table evidence strings, not their questions, and empty predicted/gold evidence can receive full evidence credit. Write an adapter for its JSONL prediction format (`question_id`, `predicted_answer`, `predicted_evidence`), including its special `Unanswerable` answer value. Convert source paragraph IDs back to original evidence strings for that scorer. Never encode a provider error as `Unanswerable`; retain the failure record and score it as a failed prediction. Inspect the pinned evaluator's exact format and add fixture tests for the adapter. Keep its official score separate from your product metrics.

**Commands:**

```powershell
python -m evidence_assistant.cli evaluate-retrieval --split validation --manifest data/manifests/validation_pilot.json --methods bm25 dense hybrid
python -m evidence_assistant.cli evaluate-qa --split validation --method hybrid
python -m evidence_assistant.cli report --run-dir reports/runs/RUN_ID
python -m pytest tests/test_evaluation.py -q
```

Each evaluation command should also accept `--config config.yaml` and a manifest path, defaulting to the saved pilot selection. Implement a `freeze` command that writes the configuration, prompt, scoring-policy, dataset-manifest, and model/index hashes to a run manifest and prints its SHA-256. Final test evaluation must require `--split test`, `--manifest data/manifests/test_pilot.json`, and `--frozen-run-manifest PATH`; reject a run if the current settings differ from that manifest. For example, after Task 7's validation decisions:

```powershell
python -m evidence_assistant.cli freeze --config config.yaml --output reports/runs/frozen_candidate.json
python -m evidence_assistant.cli evaluate-qa --split test --manifest data/manifests/test_pilot.json --method dense --frozen-run-manifest reports/runs/frozen_candidate.json
```

**Check:** Results are reproducible and question-level errors are inspectable. No fabricated target score is necessary to call the evaluation complete.

### Task 7 — Diagnose failures and make one justified improvement

**Modify:** Retrieval/chunking/prompt settings as justified. **Create:** `reports/failure_analysis.md`.

- [x] Review the validation failures and assign a primary cause: ingestion loss, chunking, retrieval miss, partial evidence, wrong interpretation, unsupported claim, over-refusal, or service error.
- [x] Choose one dominant problem to address. Examples: hybrid retrieval for rare method names; a reranker for semantically similar but irrelevant passages; a changed context budget for answers needing multiple paragraphs.
- [x] State the hypothesis before running the change and change one major factor at a time.
- [x] Compare against the frozen baseline on the same validation cases and report quality, latency, and resource tradeoffs. Keep a change only when the evidence justifies it; document regressions as well as gains.
- [x] Decide on an optional **oracle-context diagnostic** (not run; no more model tests requested). This would run with gold evidence on a separate offline path to estimate how much failure is caused by retrieval. Label it clearly and use the same question slice. It is never a user-facing feature or a fair score for the normal pipeline.
- [x] Freeze the final candidate and complete the held-out pilot: 187/187 attempted, with the two original rate-limit failures retained and no unattempted cases. The user authorized the final 33 calls; all original 154 records remain intact. Publish the complete scores and denominators. If later changes use that test's answers, call it a development set and create a genuinely new held-out evaluation.

**Check:** The report explains what changed and why. If the more complex system loses to BM25, retain and report the stronger simple baseline.

### Task 8 — Expose the evaluated pipeline through FastAPI

**Create:** `api.py` and `tests/test_api.py`. **Reuse:** `answer_question`; do not create a separate API-only answer algorithm.

| Endpoint | Contract |
| --- | --- |
| `GET /health` | Process is alive; returns 200 without claiming model readiness. |
| `GET /ready` | Returns 200 when the configured corpus/index/model adapter is ready; 503 with a specific unavailable dependency otherwise. |
| `GET /papers` | Returns indexed paper IDs, titles, and section metadata. |
| `GET /papers/{paper_id}/paragraphs/{paragraph_id}` | Returns stored source text for an existing paragraph of that paper. |
| `POST /questions` | Accepts `paper_id` and `question`; uses the configured retrieval method and returns `AnswerResult`. |

- [x] Test an ordinary answer, an appropriate insufficient-evidence result, an unknown paper, a mismatched paragraph/paper pair, an empty question, and a provider timeout.
- [x] Bound question length to 2,000 characters. Return 422 for invalid request fields, 404 for unknown papers/paragraphs, and a specific 502/503 error for invalid model output or unavailable services.
- [x] Load models and indexes once into application state rather than reloading them for every question.
- [x] Verify that API results and offline evaluation use identical core service behavior. Mark fake-model tests clearly and retain a small explicitly enabled live integration smoke test.
- [x] Include request IDs in responses and logs. Do not expose environment secrets or internal exception traces in API errors.

**Commands:**

```powershell
python -m uvicorn evidence_assistant.api:app --host 127.0.0.1 --port 8000
python -m pytest tests/test_api.py -q
```

Use `/docs` locally to inspect the request/response contracts. An unavailable model is an operational error, not evidence that a research question is unanswerable.

### Task 9 — Build the evidence viewer and ask someone to use it

**Create:** `ui.py`, demo instructions, and a short usability note.

- [x] Add a searchable paper selector and a single question input.
- [x] Display the validated claims in readable prose, with evidence links beside the relevant claims.
- [x] On citation selection, show the paper title, section, original paragraph, and highlighted chunk span. Keep the original text available so a user can check surrounding context.
- [x] Show insufficient-evidence and service-error states differently. Do not turn “source span exists” into a green correctness badge.
- [x] Display response time and put model/index details in an optional technical-details panel.
- [x] Record peer feedback status: explicitly deferred by the user on 27 October 2026. When resumed, ask two or three peers to use the assistant on unfamiliar papers. Record their questions, confusing behaviors, and whether the evidence helped them verify an answer. Treat this as exploratory feedback, not statistically demonstrated productivity improvement.
- [x] Record a short captured-frame walkthrough showing a supported answer, an unanswerable question, a failure, and how the evidence viewer makes that failure inspectable.

**Command:**

```powershell
python -m streamlit run src/evidence_assistant/ui.py
```

The UI calls the API. A UI change must not silently change the retrieval or generation configuration used in your published results.

### Task 10 — Package, reproduce, and publish the finished work

**Create:** `Dockerfile`, `compose.yaml`, CI workflow, README, data/model cards, and release report.

- [x] Build a CPU-capable application image from the tested lock file. Keep dataset/model acquisition as an explicit setup step, then mount the prepared corpus/index artifacts for runtime use.
- [x] Define API and UI services. The UI uses `http://api:8000` inside Compose. Configure the hosted provider key at runtime through an ignored environment file; do not copy it into the image. Verify outbound provider access from the API container. Bind demo ports to localhost.
- [x] Mount corpus/index files read-only where practical and put run logs in a separate writable location. Do not mount benchmark references into the application container.
- [x] Add CI for linting and deterministic unit/integration tests using synthetic fixtures and fake model responses. Keep network/model-download tests separately enabled.
- [x] Verify startup and the complete question-to-citation flow using synthetic responses in a clean Linux image; verify real stored sources survive restart. New hosted generation is explicitly omitted under the user's instruction to stop model tests. Document model downloads and hardware requirements separately from container startup.
- [x] Give the README: problem, intended user, short demo, architecture, setup commands, data provenance/license, evaluation protocol, result table, failure examples, limitations, and your contribution.
- [x] Record model revisions/digests, corpus/index hashes, prompts, run IDs, dependencies, hardware, and evaluation denominators in `reports/evaluation.md`.
- [x] Include QASPER attribution and its CC BY 4.0 data terms separately from your code license. Review licenses of any reused code and model weights. [Dataset card and license](https://huggingface.co/datasets/allenai/qasper)
- [x] **Published 31 October 2026:** Code and reproducibility instructions are public on GitHub. Large raw datasets, private PDFs, model assets, keys and private run logs remain excluded; selected non-sensitive examples and clearly labeled audits are included.

Local packaging and public source publication are complete. See `reports/release.md`
for checks, chronology and explicit acceptance limits. Public application hosting
and independent human quality review are not claimed.

**Final local checks:**

```powershell
python -m ruff check .
python -m pytest -q
docker compose up --build
```

Then manually reproduce one supported answer, one insufficient-evidence response, and one controlled service failure. Confirm that citations still open the same stored source text after restarting the application.

## 8. What to put in the evaluation report

Use an initially blank results table like this:

| Run | Retrieval | Model/prompt | Questions | Evidence Recall@5 | Answer F1 | Audited claim support | False-refusal rate | System-error rate | Warm p95 latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline A | BM25 | Record exact versions | Measure | Measure | Measure | Measure | Measure | Measure | Measure |
| Baseline B | Dense | Same model/prompt | Same cases | Measure | Measure | Measure | Measure | Measure | Measure |
| Candidate C | Hybrid | Same model/prompt | Same cases | Measure | Measure | Measure | Measure | Measure | Measure |

Below it, state:

1. Which split and paper/question manifests were used.
2. How many cases were included in each metric and how many were excluded, with reasons.
3. Whether a metric covers the full selected set or a declared text-only subset.
4. How multiple references, disagreements, empty evidence, and errors were scored.
5. Which questions were manually audited and how support was judged.
6. Whether timing includes model loading, caching, and network calls.
7. What remains uncertain: public-benchmark contamination, annotator incompleteness, model variation, and sample size.

For uncertainty estimates, bootstrap by paper rather than treating questions from the same paper as independent. With a small pilot, emphasize counts and failure examples instead of claiming general superiority from a tiny score difference.

## 9. Common mistakes to avoid

| Mistake | Correction |
| --- | --- |
| Embedding the entire dataset row | Export document-only text before indexing; keep `qas` and answers in the evaluator. |
| Assuming a citation proves truth | Validate source locations mechanically and audit claim support separately. |
| Treating retrieval failure as dataset unanswerability | Record the system's abstention, then score it against the independent reference label. |
| Choosing only easy papers/questions | Save deterministic paper selections and retain all their questions. |
| Combining annotator evidence into a required union | Preserve alternate references and score against individual reference sets. |
| Claiming PDF page citations from paragraph labels | Use section/paragraph citations until PDF coordinates are independently implemented and checked. |
| Installing the historical QASPER training stack as the application's foundation | Use the released JSON and a current, minimal stack; the old baseline repository is a reference for evaluation. |
| Relying on an unverified `load_dataset("allenai/qasper")` call | The Hub still lists a legacy loader script, and newer Datasets versions removed script loading. Use the explicit archive adapter in Task 2 or verify and pin a supported Parquet route. [Datasets 4.0 release notes](https://github.com/huggingface/datasets/releases/tag/4.0.0) |
| Giving each retrieval method a different model or larger context | Hold generation and context policy fixed, then compare the retrieval change. |
| Showing only successful screenshots | Include misses, unsupported claims, and unnecessary refusals in the published analysis. |
| Building many agents before evaluating retrieval | Establish a measured pipeline first; expand only to address a demonstrated problem. |

## 10. Later extensions, in priority order

Choose one extension only after the first version is complete.

The database roadmap is SQLite first, followed by a planned PostgreSQL migration in a later version. Complete and evaluate the SQLite application before beginning that migration.

1. **PDF ingestion follow-up:** Selectable-text uploads and arXiv imports are implemented. OCR, region coordinates and extraction-quality/QA evaluation on new documents remain future work. Keep extraction quality and QA quality as separate measurements.
2. **Cross-paper discovery and comparison:** Add a paper-retrieval stage and a collection-level relevance test set. QASPER's supplied-paper scores do not establish collection-search quality.
3. **Retrieval/reranker fine-tuning:** Use training annotations and paper-disjoint validation, mine negatives from training documents, and compare against the unchanged pretrained baseline. Keep final test labels held out.
4. **Persian questions or documents:** Build an independently checked Persian evaluation set; measure the relevant language pairs. Translation alone does not establish Persian retrieval/answer quality.
5. **Migrate SQLite to PostgreSQL and add document versions:** Transfer existing paper metadata, paragraphs, chunks, and run records while preserving stable IDs and citation source spans. Verify record counts, source hashes, and the question-to-citation flow after migration, and document a rollback path. Demonstrate schema migrations, useful analytical SQL over runs, and invalidation of stale citations when a document changes.

## 11. Honest résumé and interview presentation

Use measured facts once the project is finished. For example:

> Built a research-paper QA application with paragraph-linked evidence and insufficient-evidence handling; compared BM25, dense, and hybrid retrieval on a held-out QASPER subset and published answer/evidence evaluation, failure analysis, and latency measurements.

Replace general wording with your actual sample size and measured results when available. A second bullet can describe the FastAPI service, source-span validation, and reproducible container if you built and tested them.

Do not invent improvements, describe a local demo as enterprise production, or claim hallucinations were eliminated. Explain one failure you diagnosed and one design choice you changed because of evidence. That will give an interviewer something concrete to assess.

## 12. Primary references

- [QASPER dataset card, schema, and license](https://huggingface.co/datasets/allenai/qasper)
- [Original QASPER paper](https://aclanthology.org/2021.naacl-main.365/)
- [Official v0.3 archive URLs and loader](https://huggingface.co/datasets/allenai/qasper/raw/main/qasper.py)
- [Official dataset split metadata](https://huggingface.co/datasets/allenai/qasper/blob/main/dataset_infos.json)
- [Official QASPER baseline repository](https://github.com/allenai/qasper-led-baseline)
- [Official evaluation implementation](https://raw.githubusercontent.com/allenai/qasper-led-baseline/main/scripts/evaluator.py)
- [MiniLM embedding model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Groq OpenAI-compatible API](https://console.groq.com/docs/openai)
- [Groq structured outputs](https://console.groq.com/docs/structured-outputs)
- [Groq Free Plan rate limits](https://console.groq.com/docs/rate-limits)
- [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Streamlit chat input](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input)
- [Docker Desktop networking](https://docs.docker.com/desktop/features/networking/)

Implementation choices and suggested milestones are the author's recommendations. Source specifications were checked on 26 October 2026; verify installation compatibility and access when you begin.
