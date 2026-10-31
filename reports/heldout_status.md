# Held-out pilot — completed on 27 October 2026

All **187/187** selected cases have been attempted: **116 answered,
69 insufficient-evidence responses, and 2 retained service errors**.
There are **zero unattempted questions**. This is the 50-paper pilot, not the full
official QASPER test split. No failed case was regenerated or dropped.

The user initially stopped inference at 154/187, then explicitly requested finishing
the remaining 33 on 27 October 2026. The 33 new attempts completed with
0 new errors. The original 154 prediction records remain
byte-for-byte intact, including both historical HTTP 429 failures. Those failed
cases stay in the denominator and receive official Answer F1 zero.

## Results

| Metric | All 187 selected questions | Strict text-only: 149 questions |
| --- | ---: | ---: |
| Official Answer F1 | 0.2600 | 0.2938 |
| Official Evidence F1 | 0.4374 | 0.4928 |
| Answer coverage | 116/187 (62.03%) | 100/149 (67.11%) |
| Structurally valid citations | 178/178 (100.00%) | 154/154 (100.00%) |
| False refusals on consensus-answerable questions | 54/162 (33.33%) | 34/126 (26.98%) |
| Abstention precision on consensus-labeled refusals | 3/57 (5.26%) | 3/37 (8.11%) |
| Unanswerable recall | 3/4 (75.00%) | 3/4 (75.00%) |
| System errors | 2/187 (1.07%) | 2/149 (1.34%) |
| Unattempted questions | 0/187 (0.00%) | 0/149 (0.00%) |
| Warm end-to-end p50 / p95 | 1.31 / 2.65 s | 1.29 / 2.65 s |


Full retrieval metrics, denominators, eligibility counts, usage, and hashes are in
[heldout_summary.json](heldout_summary.json); interpretation is in
[evaluation.md](evaluation.md). Human claim-support scores remain unavailable.

## Integrity and provenance

- Candidate: Groq `openai/gpt-oss-20b` plus dense retrieval, frozen code `7788140`.
- Frozen SHA-256: `878815f1e6e4d922661b3e2932f795db4d4a7f23512d5dc27bc462b01c47eeba`.
- Run binding SHA-256: `ae4cb314e67f14e4b9695b6d8a701d9446bc2914a6dd699848160850622bcad8`.
- Final prediction SHA-256: `b45ec181bf6f910734d7a07fdaf6cb06b0a3c01d06cce36db632069be3600d60`.
- All 187 question IDs occur exactly once and match the original frozen selection.
- All 178 emitted citations were independently rechecked against original source spans.
- All 185 non-error responses match calibrated input-token counts.
- Frozen inputs, original run binding, scoring code, and consumed-selection marker are unchanged.

The original 18 Python modules were copied with exact frozen byte hashes into
`.cache/frozen-heldout-evaluator/`. The unchanged evaluator used original absolute
asset/configuration/output paths, excluding later API/UI/export modules from the
frozen source inventory. It resumed only missing IDs at 20-second intervals.
No configuration, prompt, budget, retrieval, model, or scoring change was made.
The provider's returned fingerprints remain recorded; hosted weights cannot be pinned locally.

Raw run/checkpoint: `reports/runs/final-test/`. Pre-resume backup:
`.cache/heldout-before-authorized-resume/`. Sanitized operational log:
`.cache/final-test-authorized-resume.log`. The original consumed-selection marker
must remain intact; this held-out selection is finished and must not be rerun or
used for subsequent tuning without declaring it development data.

To regenerate scores from saved predictions without model calls:

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli report --run-dir reports/runs/final-test
```

Completion does not authorize additional model comparisons, live API smoke tests,
human/peer review, or publication. Their existing scope decisions remain in effect.
