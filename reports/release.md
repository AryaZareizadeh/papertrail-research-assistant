# Local release verification — 27 October 2026

## Scope and decisions

PaperTrail 0.1.0 provides one-paper question answering through FastAPI and a
Streamlit evidence viewer. Groq GPT-OSS-20B with dense retrieval is the selected
configuration. SQLite is the initial store; PostgreSQL remains future work.
The user accepted the labeled agent claim audit, stopped further model testing,
and explicitly deferred peer feedback. Those limits are retained in the
[evaluation report](evaluation.md) and [usability notes](usability.md).

Task 7 closes with an incomplete held-out pilot: 154/187 attempted, two retained
HTTP 429 errors, 33 unattempted; no complete held-out score is claimed. The reviewed
API was integrated at `2e75db6`; the reviewed UI/demo at `d813dec`. The original
frozen run, checkpoint, consumed marker, and source identities remain preserved.

## Verified locally

- API/UI shared behavior and source validation have deterministic fixtures.
- UI selection, claim/source navigation, Unicode spans, escaping, paper-change
  clearing, and separate refusal/error states work with fake responses.
- Actual browser captures demonstrate a saved training answer and original text,
  plus explicitly simulated refusal/error states. The 18-second GIF is a sequence
  of captured frames, not a continuous screen recording or a new model measurement.
- Fresh UI review's malformed HTTP error-code crash was reproduced with two RED
  cases and fixed; the full Windows suite passed 146 checks before export was added.
- Runtime export's four synthetic checks passed. It copied 26 hash-verified runtime
  files, preserved original assets/calibration, and rewrote only snapshot paths for
  the container. No benchmark references, provider keys, or private logs were copied.
- A CPU image built from the lock with `torch==2.14.1+cpu`. Docker Desktop 29.5.3,
  Linux containers, Python 3.13.15. Both Compose services became healthy.
- Final Windows checks: Ruff passed; 150 deterministic checks passed, two hosted
  tests skipped. In the image, 150 deterministic checks passed with networking disabled, using
  clean Python test source files without host bytecode; two hosted tests skipped.
- Container readiness, all 85 paper summaries, and three original paragraphs
  matching the saved citation spans passed real HTTP checks.
- Authenticated Groq `GET /models` returned 200 from the API container. This is a
  connectivity/credential check, not answer-generation inference.
- Packaging review found two important issues: export destinations inside prepared
  model snapshots could recursively copy, and a fresh Linux log volume was not
  writable by UID 10001. Both were reproduced before fixing them in one pass.
  Export now rejects overlaps before creating directories; the Docker-managed log
  volume inherits the image directory's application-user ownership. The fresh
  offline-container write probe passed after failing on the previous image.
- Both services restarted healthy. All three source hashes remained identical,
  and a log marker survived the restart. Runtime assets are read-only, no benchmark
  reference directory is mounted, and the UI receives no provider credentials.

The Python base is pinned to digest
`sha256:8d9d0b8bcf6506481eae4907c18f5e3e7902e629f5f6d684f9e7c32e85e3ddf0`.
The dependency lock, model revisions, and original frozen artifacts are recorded
in source and [the evaluation report](evaluation.md). GitHub Actions checkout and
setup-python are pinned to resolved v7 commits. CI is configured, not claimed to
have run on GitHub.

The reviewed image ID is
`sha256:de3d803af690c8abaca8947a65ee39a0b0f561249cd57f858f1feb2130d279f3`.
Current local services use API port 18000 and UI port 18501 to avoid the separate
offline demo on 8501. Compose defaults remain 8000/8501 for a fresh start.

## Explicit limits and publication status

Final packaging review and rebuilt-image startup/source persistence checks passed.
The hosted API generation smoke
remains deliberately unrun under the user's instruction. No human claim-support
or peer-usability score is available. One deferred API minor: malformed UTF-8
JSON receives a generic HTTP 400/internal-error code; it exposes no traces.

There is no Git remote configured. Code and reproducibility instructions are
prepared locally; no repository push, public deployment, or GitHub release has
been performed. The user explicitly deferred publication to try and improve the
app first and will request publication later. This closes local packaging with
publication deferred, rather than claiming a public release.
