# Implementation and experiment log

## 2026-10-26 — Initial implementation

Plan: `PaperTrail_Development_Guide.md`; binding specification: its Section 2.
The user approved implementing the guide, including SQLite first and PostgreSQL later.

### Pre-flight interfaces

| Tasks | Shared contract | Decision |
| --- | --- | --- |
| 1 → 2–10 | AppConfig and typed records | Pydantic records; all paths resolve against the config file. |
| 2 → 3, 6 | Corpus vs evaluation exports | Separate directories and consumers; stable positional IDs. |
| 3 → 4, 5 | Chunks and stored source offsets | Python half-open character offsets; original text preserved. |
| 4 → 5, 6 | RetrievedChunk and IndexManifest | Paper filtering before ranking; validate artifact compatibility. |
| 5 → 6, 8, 9 | AnswerResult and shared service | Separate abstentions from errors; citations built from storage. |
| 6 → 7, 10 | Frozen run manifests | Validation choices precede held-out test; report failed cases. |

Ruling: Initialize a new feature branch in this requested directory; no existing
repository/worktree exists to isolate. Cost if wrong: branch/directory relocation.

Ruling: The existing approved guide supplies both specification and task plan;
do not repeat design questions. Cost if wrong: later amendments to the guide.

Environment: Python 3.13.0 on Windows. `python -m venv` created the interpreter
but bundled `ensurepip` failed; use uv to install into the environment. Dependency
downloads require network access beyond the restricted shell sandbox.

### Task status

- Task 1: complete — package, configuration, schemas, CLI, doctor, full dependency
  installation, and `requirements.lock.txt` verified. All 80 dependency versions
  reproduced exactly in a fresh `.venv-repro`; 47 tests passed there.
- Task 2: complete — downloaded official archives, preserved archive/source hashes,
  normalized isolated corpus/evaluation records, verified split counts, saved pilot
  selections, and read five training examples. No test answers were inspected.
- Task 3: complete — real pinned MiniLM tokenizer produced 4,440 chunks from
  4,043 paragraphs across 85 pilot papers. Every stored source span was checked;
  maximum actual input was 194 tokens including special tokens, below limit 256.
  Chunking manifest and rejection/statistics records saved locally.
- Task 4: BM25 works on real pilot papers; ten training-question results inspected.
  Dense/hybrid mechanics and index integrity have deterministic synthetic tests.
  Actual dense/hybrid model loading, indexing, and retrieval are pending.
- Tasks 5–10: pending; no generated answers, benchmark scores, API, UI, or Docker
  readiness claimed.

Ruling: While runtime dependencies download, implement and test the standard-library
and lightweight ingestion path. Configuration/CLI tests already pass; no ingestion
depends on the downloading model stack. Cost if wrong: re-run after full installation.

### Setup decisions and verification

Ruling: Split explicit tokenizer acquisition (`prepare-tokenizer`) from full model
acquisition (`prepare-embedding`) after large downloads stalled. Keep complete
runtime dependencies declared, and verify a separate `requirements.bootstrap.lock.txt`
for the SQLite/BM25 milestone. Cost if wrong: repeat full-stack setup before dense
retrieval or generation; bootstrap results do not establish full-stack readiness.

Ruling: Publish immutable, content-addressed embedding filenames through the index
manifest rather than overwrite `embeddings.npy`. Cost if wrong: unused old/orphan
vector files need eventual cleanup; manifest-aware loading is required.

Environment: NVIDIA RTX 3050 Ti laptop GPU, 4096 MiB VRAM; 16,782,188,544 bytes system
RAM observed. No generation throughput, memory requirement, or model quality inferred.

TDD evidence: missing config/data/chunk/store/retrieval modules failed before their
implementations. Additional real failures demonstrated YAML tracebacks and missing
archive provenance; both were corrected and the suite rerun.

Fresh independent review identified six issues, each reproduced RED then fixed:

1. Enforce the encoder's actual input limit before encoding.
2. Bind chunks to the resolved tokenizer/model revision and effective input limit.
3. Reject stale chunk settings for BM25 as well as dense retrieval.
4. Validate archive contents in staging before replacing source files.
5. Preserve the previous working index if new manifest publication fails.
6. Reject chunk section labels that disagree with their source paragraph.

Final review fix pass: 45/45 tests passed; subsequent tokenizer adapter coverage
brought the suite to 47/47. No deferred review findings. The tokenizer-only path
was separately checked against the real cached MiniLM tokenizer.

Reproduction: `.venv-verify` was created fresh; all 32 pinned bootstrap packages
installed from `requirements.bootstrap.lock.txt`, then the local package installed
editable without full dependencies. Full suite: 47 passed in that environment.
Ruff passed. CLI help/doctor and a real paper-scoped BM25 query passed there too.

See `training_retrieval_notes.md` for corpus counts and qualitative retrieval misses.
No quality improvement has been claimed. Next: finish full dependency/model setup,
verify real dense/hybrid retrieval and timing, then implement the evaluated answer
pipeline before adding the API and UI.

## 2026-10-26 — Checklist audit, starting at Task 1

Task 1: all eight checkboxes verified in order. Configuration tests: 16 passed.
CLI help/doctor and ignore rules passed. Full runtime dependency install succeeded
after retrying with four concurrent downloads and 180-second HTTP timeouts.
Primary environment: 81 compatible installed packages including this project.
Import/operation smoke: PyTorch 2.14.1+cpu, NumPy 2.1.2, Sentence Transformers 6.2.0,
Transformers 5.20.2, FastAPI 0.162.0, and Streamlit 1.66.1 loaded; matrix operation
returned the expected result. The lock contains 80 dependency pins, excluding this
editable project and machine-specific paths. It was installed into a fresh
`.venv-repro`; all 80 versions matched exactly, `uv pip check` passed, and the full
47-test suite passed. Local verification required an unrestricted retry after
Windows sandbox permissions blocked a PyTorch launcher, with no network needed.

Next audit: Task 2's real archives, split isolation, runtime/evaluation boundaries,
pilot selection, and retained-question counts.
