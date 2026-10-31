# Sequential checklist audit

Updated: 31 October 2026. Task entries record acceptance closeout, including
explicitly stated user waivers and deferrals; they do not imply every original
acceptance check ran. All 80 guide items are closed, with publication authorized
and completed on 31 October. The original readiness snapshot is in
[readiness_audit.md](readiness_audit.md); current feature checks are in
[paper_import_verification.md](paper_import_verification.md) and
[authorship_fix.md](authorship_fix.md).
The per-task test counts below are historical milestone results; the current
deterministic suite passes 195 tests with two hosted checks skipped.

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
- [x] Task 7 — Failure analysis, selection, and completed held-out pilot.
  Controlled validation comparisons selected Groq GPT-OSS-20B plus dense retrieval.
  On the user's explicit completion request, the remaining 33 held-out cases
  completed with 0 new errors: 187/187 attempted, 2 original throttles retained,
  zero unattempted. All original 154 records, frozen inputs, and consumed marker
  are unchanged. Whole-pilot Answer F1: 0.2600. See evaluation.md and heldout_status.md.
- [x] Task 8 — Integrated FastAPI service; live API generation remains unrun.
  Draft saved separately at d004ee3 on codex/api-draft. Fresh review fixes verified
  RED→GREEN; 137 tests pass in both dependency environments, two live tests skipped.
  Integrated at2e75db6. Real read-only HTTP/source/docs checks pass. The live API
  question smoke remains unrun under the user's no-more-model-tests instruction.
- [x] Task 9 — Evidence viewer and recorded walkthrough; peer feedback deferred.
  Searchable paper selection, claims/source buttons, escaped Unicode-span highlights,
  original text, separate error/refusal states, latency, and technical details work.
  AppTest verifies source selection does not regenerate and paper changes clear
  prior answers. Fresh review's malformed-error-code crash was reproduced then
  fixed; 146 deterministic checks passed, two hosted tests skipped. Real narrow-
  browser walkthrough and four captured states are saved in reports/demo/.
  The user explicitly deferred peer feedback; no human usability result is claimed.
- [x] Task 10 — Local packaging complete; public source published on 31 October.
  CPU Docker image and separate API/UI services are running. Runtime assets are
  mounted read-only, logs use a writable Docker volume, and no benchmark labels or
  keys enter the image. Final review's two important bugs were reproduced and fixed.
  Windows and offline Linux suites each pass 150 checks; two hosted tests skip.
  Restart/source/log persistence checks pass. CI, README, licenses, data/model cards,
  and release notes are prepared. Live generation stays unrun by user instruction.
  After trying the app, the user requested public GitHub publication. Source and
  reproducibility instructions are now at
  [AryaZareizadeh/papertrail-research-assistant](https://github.com/AryaZareizadeh/papertrail-research-assistant).
  Keys, imported PDFs, large assets and private run logs are excluded. The current
  local suite passes 195 tests, 2 hosted skipped. Public app hosting and independent
  human claim-support review remain outside this publication. See release.md.
