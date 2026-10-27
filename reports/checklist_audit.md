# Sequential checklist audit

Date: 26 October 2026. Checkboxes reflect completed acceptance checks, not only
the presence of implementation code.

- [x] Task 1 — Project, configuration, full dependencies, and reproducible lock.
  Verified all eight guide items; 16 configuration tests and 47 total tests pass.
  All 80 dependency versions reproduced in a fresh environment; dependency checks,
  CLI help/doctor, ignore rules, and runtime import/operation smoke passed.
- [x] Task 2 — Archive hashes, isolation, selections, and question retention.
  All five archive/source hashes match; all 83,079 original paragraphs/abstracts
  match the exports. Runtime schemas exclude annotations. All 5,049 questions and
  annotation counts are retained; official split assignments are disjoint.
  Deterministic pilot counts: 5/19 train papers/questions, 30/92 validation,
  50/187 test. All eight data tests pass.
- [x] Task 3 — Source offsets, tokenizer limits, and SQLite integrity.
  All 4,440 chunks match their original spans and sections; every nonblank
  paragraph has complete character coverage. SQLite integrity/foreign-key checks
  pass. Maximum actual input is 194 tokens against the pinned 256-token limit.
  All 13 chunk/store/pipeline/tokenizer tests pass; full suite remains 47/47.
- [x] Task 4 — Real dense/hybrid indexing and retrieval measurements.
  Pinned MiniLM weights built a normalized 4,440 × 384 index. All three methods
  returned only the selected paper's chunks on ten training questions. Model load,
  index build, artifact load, and warm-query timings were measured separately.
  Eleven retrieval tests and 48 total tests pass. Exploratory timing only; no
  benchmark superiority claimed.
- [x] Task 5 — Answer generation and citation validation; live Groq verified.
  Hosted Groq adapter, immutable source citations, bounded retries, refusals vs
  errors, prompt-injection data boundaries, whole-chunk budget trimming, and
  separate SQLite/JSON run records are tested. Pinned GPT-OSS tokenizer prepared.
  Live training-paper smoke passed with exact source citations. Three calibration
  prompts consistently required an offset of -11 tokens; an independent fourth
  prompt matched exactly at 908 tokens. Persisted calibration reconstruction also
  matched. Current suite: 77 passed; one opt-in live test skipped in ordinary runs.
  The explicitly enabled live test passed separately. Quality evaluation is next.
- [x] Task 6 — Evaluation pipeline and accepted agent audit.
  Scoring fixtures, official scorer adapter, eligibility mapping, shared-budget
  retrieval, checkpoint/resume, report integrity, and frozen test gates implemented.
  All 92 validation questions compared across retrieval methods. Three-question
  hosted timing sample and all 90 cases in the 30-question/three-method batch
  completed. All actual token counts matched calibration. Thirty hybrid responses
  source-reviewed with explicit agent labels; human claim support remains unreviewed.
  Real artifact freeze passed; changed weight/tokenizer/vector bytes are rejected.
  Versioned rescoring preserves original reports and exactly matches their metrics.
  Current suite: 102 passed, one opt-in live test skipped, in both environments.
  User accepted the clearly labeled agent audit for now. Human support stays
  unavailable. Final candidate/test evaluation follows Task 7 decisions.
- [ ] Task 7 — Failure analysis and a measured improvement.
  All 30 fixed-context model comparisons and agent inspections completed. Nemotron
  improved F1/refusals but had five rate-limit errors, so Groq remains active.
  Dense is the strongest measured Groq retrieval baseline, with recorded tradeoffs.
  User confirmed Groq GPT-OSS-20B as the selected generator. Dense retrieval stays
  selected. Held-out evaluation stopped at the user's request: 154/187 attempted,
  including two retained throttles; 33 intentionally unattempted. No more model
  tests are requested. Remaining work is reporting/acceptance closeout with the
  incomplete pilot clearly labeled, not more inference. See heldout_status.md.
- [ ] Task 8 — FastAPI service.
  Draft saved separately at d004ee3 on codex/api-draft. Fresh review fixes verified
  RED→GREEN; 137 tests pass in both dependency environments, two live tests skipped.
  Real read-only HTTP/source/docs checks pass. Integrate the reviewed draft into
  the main project. The live API question smoke remains unrun under the user's
  no-more-model-tests instruction; record that limit instead of blocking on it.
- [ ] Task 9 — Evidence viewer and usability feedback.
- [ ] Task 10 — Packaging, reproducibility, and release.
