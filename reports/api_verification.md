# API verification — 27 October 2026

Task 8 was prepared in a separate worktree, based on `7788140`, reviewed and saved at
`d004ee3`, then integrated into the main project at `2e75db6`. The user stopped
further model testing and selected Groq GPT-OSS-20B. The user later explicitly
authorized finishing the original held-out pilot, now complete at 187/187 attempts;
see [the evaluation report](evaluation.md). The separate live API smoke remains unrun.

The shared `answer_question` function supplies every API answer. Synthetic tests
compare its offline result to the API result, excluding only latency/request ID.
The application initializes its catalog, retrieval model, token counter, and
provider adapter once. No benchmark references are used by this runtime path.

Verification in both the primary and independently reproduced Windows/Python 3.13
environments: **137 passed, two opt-in live tests skipped**. Ruff passes. Commands:

```powershell
python -m pytest -q --basetemp .cache/pytest-api-reviewed
python -m ruff check .
git diff --check
```

Real Uvicorn startup was checked with the prepared 85-paper corpus, pinned model
artifacts, and Groq configuration. Read-only HTTP probes returned health/readiness
200, 85 paper summaries, original source text, 404 for a mismatched source, and
working `/docs`/OpenAPI error contracts. Every response carried a request ID.
These checks made no provider calls. The server used an ephemeral localhost port.

A fresh read-only reviewer found three important issues. All were reproduced
before fixes and verified by six regression cases:

- Storage, validation, and unexpected exceptions now adopt the core's persisted
  request ID; response, header, and logs remain correlated.
- A malformed path value such as `artifact_dir: null` leaves liveness available
  and readiness unavailable with a controlled configuration code.
- BM25 readiness does not require dense-index/model metadata. Production token
  calibration remains mandatory for every method.

Deferred minor: malformed UTF-8 request bodies currently receive HTTP 400 with a
generic `internal_error` code. They do not expose raw input or traces; a clearer
invalid-request code is a later polish item. Ordinary JSON validation returns the
documented sanitized 422 envelope.

The opt-in live API smoke uses one training-paper question and checks that every
citation resolves to the exact original paragraph span through HTTP. It has not
run, following the user's no-more-model-tests instruction. Existing live core
generation checks remain historical evidence; API/provider generation is not newly
claimed. The API is accepted with that explicit limit. See [API usage](../docs/api.md).
