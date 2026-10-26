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
- [ ] Task 3 — Recheck source offsets, tokenizer limits, and SQLite integrity.
- [ ] Task 4 — Finish real dense/hybrid indexing and retrieval measurements.
- [ ] Task 5 — Answer generation and citation validation.
- [ ] Task 6 — Evaluation pipeline.
- [ ] Task 7 — Failure analysis and a measured improvement.
- [ ] Task 8 — FastAPI service.
- [ ] Task 9 — Evidence viewer and usability feedback.
- [ ] Task 10 — Packaging, reproducibility, and release.
