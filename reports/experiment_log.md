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
- Task 4: complete — pinned MiniLM built a real normalized 4,440 × 384 index.
  BM25/dense/hybrid retrieved only the selected paper on ten training questions;
  source relevance and misses inspected. Separate load/build/warm timing recorded.
- Task 5: hosted Groq adapter, answer/citation service, pinned tokenizer, and local
  run persistence implemented and tested offline. Live API and provider token-count
  verification remain pending `GROQ_API_KEY` in the user's ignored `.env`.
- Tasks 6–10: pending; no real generated answers, benchmark scores, API, UI, or
  Docker readiness claimed.

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

Task 2 audit: all nine guide items checked. Eight data tests passed. Rehashed all
five archive/source files against the saved manifest, and compared all 83,079
paragraph/abstract exports to original source text without inspecting test-answer
content. All 5,049 questions and annotation counts are retained, paper splits are
disjoint, and runtime schemas have no benchmark annotations. Independently repeated
the pilot selection rule: train 5 papers/19 questions; validation 30/92; test 50/187.
Detailed machine-readable checks are local in `reports/runs/task2_audit.json`.

Task 3 audit: all seven guide items checked. Thirteen chunk/store/pipeline/tokenizer
tests passed. The real SQLite store passes integrity and foreign-key checks; all
4,440 chunks match original source text, ownership, section, and character offsets.
Every nonblank paragraph has complete character coverage. Duplicate text retains
distinct positional IDs. Maximum actual input: 194 tokens, below the pinned limit
of 256. Full suite: 47 passed. Details: `reports/runs/task3_audit.json`.

Task 4 audit: all eight guide items checked. Full pinned MiniLM weights downloaded;
index dimensions 4,440 × 384, normalized vectors, source/model/tokenizer manifests
validated. All three methods returned only selected-paper chunks on ten training
questions. Dense retrieval improved some inspected error-type evidence but still
missed story-evaluation evidence; this is not a benchmark improvement claim.
Fixed an observed timing-label bug with a RED→GREEN regression test: a preloaded
encoder now records zero load time and excludes it from index-build timing.
Eleven retrieval tests and 48 total tests pass, including in `.venv-repro`.

CPU smoke timing (10 training queries/method, PyTorch 2.14.1+cpu, 10 threads):
initial index build 68.58 s total, model/library load 11.68 s, build excluding load
56.90 s, embedding encoding 55.44 s. Warm query p50/p95: BM25 3.69/4.81 ms,
dense 51.69/129.50 ms, hybrid 35.05/51.18 ms. Sampling/warmup differences can
explain latency ordering; these figures are not representative benchmark estimates.
Detailed records: `reports/runs/task4_audit.json` and
`reports/runs/training_retrieval_comparison.json`.

User selected hosted generation and requested a free option. Official Groq docs
show a Free Plan for `openai/gpt-oss-20b`, supporting strict JSON schema output.
Published limits checked 26 October 2026: 30 RPM, 1,000 RPD, 8,000 TPM, 200,000 TPD;
actual account limits may differ. Sources: https://console.groq.com/docs/rate-limits
and https://console.groq.com/docs/structured-outputs. User will put `GROQ_API_KEY`
in the ignored project `.env`; no key content is logged or committed.

Next: implement Task 5 against the hosted adapter, keeping a live model/token-budget
smoke test pending until credentials and provider behavior are verified.

### Task 5 implementation and current acceptance boundary

User chose hosted inference, requested a free option, and selected the project's
ignored `.env` as the location for `GROQ_API_KEY`. Config now targets Groq Free Plan
`openai/gpt-oss-20b`. Only its tokenizer was downloaded, at resolved revision
`6cee5e81ee83917806bbde320786a8fb61efebee`; local Harmony template tokenization
was exercised successfully. No hosted calls were made without credentials.

Implemented the same answer service for CLI and future evaluator/API consumers:
ranked context is trimmed by whole chunks; the provider receives document-only
context and a strict claim/citation schema; valid claims cite only supplied chunks;
quotes are reconstructed from checked original source spans. Provider errors,
quota failures, invalid/truncated output, and source changes remain errors rather
than evidence refusals. Mutable run JSON and `reports/runs/runs.sqlite` preserve
the corpus/index database. Source/configuration/prompt hashes, generation options,
retry attempts, safe error codes/stages, and separate estimated/actual token counts
are recorded. Unavailable actual usage is null; known usage survives rejected output.

Fresh independent review found three P2 audit gaps: discarded usage on rejected
completions, missing safe failure reasons, and incomplete run provenance. Each was
reproduced with failing tests and fixed in one pass. Additional tests cover altered
source spans, citations to dropped context, original interruption preservation,
SQLite run queries, actual output-budget violations, and missing-key CLI behavior.
Current suite: 74 passed, one explicitly gated live test skipped. Ruff and dependency
checks pass. The full lock now has 81 dependency pins (adding python-dotenv 1.2.4);
all 81 matched in `.venv-repro`, where the same suite passed.

Ruling: The adapter returns provider usage/fingerprint alongside content and parsing
is a separate function, replacing the plan's draft-only adapter signature. This
retains audit data for failed outputs. Cost if wrong: adjust internal callers; the
public `answer_question` contract is unchanged and the guide reflects the interface.

Task 5 remains incomplete: the local key is still empty and provider-added prompt
formatting has not been calibrated against actual usage. Full-prompt counts are
explicitly estimates; no fixed-token-budget comparisons or answer quality claims
are made. Follow the requested sequence and finish this acceptance check before
starting Task 6. Setup is documented in `docs/hosted_model_setup.md`.

### Task 5 acceptance completed; Groq baseline retained

The preceding credential block is resolved. The opt-in live training-paper test
passed (request c3ac4f9e1cd345aca7a9ee4d73699e41, one attempt, 709 input / 199
output tokens). Three training-paper probes consistently showed a -11-token
prompt offset. An independent fourth prompt matched exactly at 908 tokens after
calibration, and loading the persisted calibration reproduced that same count.
An unsupported annual-marketing-budget probe returned insufficient evidence.
These are functional checks, not an answer-quality benchmark.

Calibration is bound to endpoint/model/tokenizer files, prompt/schema, and request
options. A regression test verifies recovery by recalibrating without loading a
stale calibration. Ordinary suite: 77 passed, one live test skipped; the live test
passed separately. Ruff passes. The suite also passes in the reproduced environment
using a workspace temporary directory (the sandbox's default temp directory was
unwritable). Task 5 is complete for Groq; Task 6 follows.

User decision: retain working Groq/GPT-OSS as the baseline, then compare Requesty's
NVIDIA Nemotron on identical questions and saved supplied passages. Switch only if
correctness and evidence support improve with acceptable latency. No provider
switch or paid fallback has been configured. Requesty requires its own credential,
format checks, and tokenizer calibration before that comparison.

### Task 6 implementation and validation in progress

Implemented exact/whitespace-only evidence mapping with repeated-position
alternatives, separate annotators and highlighted spans, declared text-only
eligibility, consensus abstention metrics, official Answer F1 adapter, saved
passages, per-case checkpoints, immutable scoring inputs, and frozen test gates.
Official evaluator pinned to e996b6c7b1b5f95d9308a74e3586416c6e780df1 with Apache-2.0
license and SHA-256; LF attributes preserve its unmodified bytes on Windows.

A new fixture initially inherited relative evaluation/manifest paths and replaced
four generated local files (questions.jsonl, data_manifest.json, validation_pilot.json,
and test_pilot.json). The fixture now uses isolated temporary paths. Regenerated
the exports from official archives and reran Task 2 audit: all five source hashes,
5,049 questions/annotations, 83,079 original paragraphs, and pilot selections verified.
Subsequent test runs leave the real selections intact.

Independent review found three P2 issues: requested dense method could load a
BM25-only service; citation validity could pair a valid supplied ID with a different
paragraph; reports could be recomputed after scoring input/code drift. All three
were reproduced by five failing cases, fixed in one pass, and verified with the
full suite (97 passed, one live test skipped), including .venv-repro. An additional
isolated final-test gate test verifies one run, explicit selection, no limits,
and resuming without another provider call.

Real retrieval completed on all 92 validation questions. Strict positive-evidence
denominator: 66; Hit@5 BM25 29/66, dense 36/66, hybrid 37/66. Dense has higher
complete-evidence coverage than hybrid, so no single retrieval winner is claimed.
Three hosted timing probes completed without errors, with calibrated counts on
all prompts. The next declared batch uses the same deterministic 30 questions
for all three methods, paced at 14 seconds between request starts; every error,
refusal, and actual supplied passage is retained. No test inference has run.

Requesty key presence was checked without displaying its value. Both provider keys
are present in ignored .env; only Groq is active. No Requesty inference has been
requested yet. Human claim support remains distinct from agent source inspection.

### Task 6 measured baseline and review boundary

All 90 requested cases completed on the same 30 validation questions. Whole-set
official Answer F1: BM25 0.3285, dense 0.3917, hybrid 0.3417. False refusals among
23 consensus-answerable cases: 7, 6, and 5 respectively. All methods incorrectly
answered both consensus-unanswerable cases (unanswerable recall 0/2). Hybrid had
one citation_not_supplied error; this receives official F1 zero and is not counted
as a refusal. No active method/provider settings changed. All 90 prompt counts
matched calibration. Known actual usage: 94,563 input + 9,037 output tokens.

All 30 hybrid responses were inspected manually by the agent and labeled as such:
11 correct, seven partially correct, two incorrect, nine refusals, one rejected
output; 27 claims include 19 fully supported, seven partially supported, and one
unsupported. Human support metrics remain unavailable. Editable self-contained
review cards are in reports/claim_review.md; detailed metrics/limitations are in
reports/evaluation_baseline.md. A pending user question asks whether to proceed
with the explicitly agent-only audit or retain the human-review gate.

Self-audit found freeze was hashing revision/index metadata rather than actual
model bytes. Three new failing tests reproduced undetected weight/vector/tokenizer
changes; snapshots now hash these actual artifacts and reject changes. Explicit
versioned rescoring was added RED→GREEN so changed reporting code cannot silently
overwrite historical scores. Rescored retrieval/QA reports exactly match every
original method metric without any new generation. The original baseline code
checkpoint is 0e420e4; original reports and predictions remain intact. Frozen Groq
baseline SHA-256 b07979afdbbcacb5b66951ec825dcf2a103684e06d6287f244cf4f943f36aa27
records comparison inputs but does not consume the held-out pilot.

Full suite: 102 passed, one explicitly gated live test skipped, in both .venv and
.venv-repro; Ruff passes. Source changes after baseline generation affect freeze
integrity/report versioning, not the answer algorithm or prediction content.

Ruling: preserve the unmodified upstream evaluator's one trailing space to retain
its official SHA-256; scope the Git whitespace exception to that vendored file.
Cost if wrong: normalize/vendor a changed copy and publish a new scoring identity.

User decision: proceed with the labeled agent audit. Task 6 is now complete;
human-audited support remains unavailable and the guide explicitly records this
accepted review boundary. Baseline is frozen for comparison; final configuration
selection and held-out evaluation remain Task 7. Requesty/Nemotron comparison is
the next one-factor experiment, with identical saved questions and passages.
