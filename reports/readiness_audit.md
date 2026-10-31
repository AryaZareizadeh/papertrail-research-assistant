# Guide readiness audit — 27 October 2026

Historical snapshot: public source publication was subsequently completed on
31 October 2026. See [release.md](release.md#public-source-publication--31-october-2026)
for the current publication status; original checks below retain their date.

Verdict: ready for local use and user evaluation within the accepted scope.
The guide has 79 checked items and one open publication item. Several checked
items explicitly close with a user waiver or deferral, so this does not mean every
original acceptance check was completed. Publication remains deferred.

Repository audited: `416de4f` (`feat: package verified local PaperTrail release`).
The working tree was clean before this audit. Application source, the selected
configuration, models, and frozen benchmark inputs remain at that implementation
state. The user's follow-up authorized completing the original pilot; 33 new
prediction records and final scores were added, with the original 154 preserved.

## Fresh verification

| Area | Result |
| --- | --- |
| Deterministic suite | 150 passed, 2 hosted checks skipped; 15.36 seconds |
| Ruff and whitespace | `ruff check .` and `git diff --check` passed |
| Dependencies | All 81 locked package versions match; `uv pip check` reports 82 installed packages compatible, including the project |
| Source data | All five recorded raw-file hashes match; 1,585 papers, 83,079 normalized paragraphs, and 5,049 question IDs/reference counts retained |
| Runtime/gold separation | Runtime records validate against document-only schemas; source exports and stored paragraphs match original paper text; deterministic leakage tests pass |
| Pilot selection | Deterministic selections reproduce: train 5 papers/19 questions, validation 30/92, test 50/187; paper splits are disjoint |
| SQLite and chunk provenance | Integrity and foreign keys pass; 85 papers, 4,043 paragraphs, 4,440 chunks; exact spans/sections and complete nonblank source coverage verified |
| Token/vector limits | Largest actual embedding input is 194 tokens within the 256-token limit; all 4,440 × 384 vectors are finite and normalized; index hashes/order match |
| Runtime export | All 26 runtime bundle files and original metadata hashes match |
| Held-out preservation | Checkpoint, prediction hash, frozen-candidate hash, and consumed-selection marker are consistent; 187 attempts, 2 original errors retained, zero unattempted; original 154 preserved |
| Running services | API and UI containers healthy; both run as the application user with read-only root filesystems |
| Mounts | API corpus/model bundle is read-only; run logs use a separate writable volume; no benchmark-reference mount |
| Read-only HTTP | API health/readiness 200; 85 paper summaries; API docs and question route schema present; all three saved demo citations match original source spans/hashes; UI health 200 |

The running image is
`sha256:de3d803af690c8abaca8947a65ee39a0b0f561249cd57f858f1feb2130d279f3`,
matching the reviewed image in [release.md](release.md).
The current interface is [localhost:18501](http://127.0.0.1:18501), with
[API documentation on localhost:18000](http://127.0.0.1:18000/docs).

Commands used for the software checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -x -q --basetemp .cache/readiness-audit-unrestricted
.\.venv\Scripts\python.exe -m ruff check .
uv pip check --python .venv/Scripts/python.exe
git diff --check
docker compose ps --format json
```

The initial sandboxed test runs encountered repeated setup errors and stalled.
The full suite passed outside the sandbox; the redundant blocked runs were stopped.
Docker/localhost access and uv's interpreter-cache writes were explicitly blocked
inside the sandbox and passed outside it. No application test failure reproduced
in the unrestricted suite.
The ignored `.cache/readiness_audit.py` performed read-only source, artifact,
selection, checkpoint, and installed-version checks. The initial readiness audit made no hosted requests or new benchmarks. The
subsequent explicit completion request authorized 33 remaining held-out calls;
completion and frozen-input integrity are documented in heldout_status.md.

## Guide coverage and remaining limits

| Guide tasks | Evidence and status |
| --- | --- |
| 1–4: setup, ingestion, chunks, retrieval | Implemented; deterministic tests and prepared-asset integrity verified above |
| 5: generation and citations | Adapter and validation implemented; historical live core smoke recorded; fresh deterministic citation/transport tests pass |
| 6: evaluation | Retrieval and generation comparisons, scoring fixtures, freezing/checkpoints, and 30-response labeled agent audit implemented; human support measurements unavailable |
| 7: improvement and held-out pilot | Groq plus dense selected on validation; held-out completion subsequently authorized and verified at 187/187 attempts; original errors retained; Answer F1 0.2600 |
| 8: FastAPI | Integrated and ready with real local assets; fresh synthetic suite and read-only HTTP pass; live API generation smoke deliberately unrun |
| 9: evidence viewer | Implemented with interaction tests and existing captured walkthrough; peer feedback explicitly deferred; no new browser walkthrough performed in this audit |
| 10: packaging/publication | Local CPU Docker packaging and runtime checks pass; earlier Linux offline/restart verification is recorded in release.md; CI configured but not run on GitHub; publication deferred and no remote configured |

The completed held-out pilot provides measured results for this selected sample.
The two separate opt-in hosted tests remain skipped. Human claim-support review,
peer usability feedback, and publication remain deferred. The small pilot and known
answer/refusal failures limit quality claims; see [evaluation.md](evaluation.md).

The guide's stale claims that implementation was only through Task 6, the held-out
run was still in progress, and the API awaited integration have been corrected.
The historical failure-analysis ending and checklist introduction now agree with
the accepted final status. The publication checkbox remains visibly open.
All checked local Markdown links resolve after these documentation changes.
