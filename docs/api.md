# Local API

The API calls the same `answer_question` function as the CLI and evaluator. The
configured retrieval method is used for every request; clients cannot override
the evaluated model, prompt, or retrieval settings.

After completing the artifact preparation steps in the README, run from the
repository root:

```powershell
python -m uvicorn evidence_assistant.api:app --host 127.0.0.1 --port 8000
```

`PAPERTRAIL_CONFIG` can point to a configuration file elsewhere. Paths inside that
file resolve against its directory. The provider key is read from the configured
environment variable or ignored `.env` file. Never put a key in a question, URL,
or tracked configuration. Runtime use reads the document corpus and prepared
model/index artifacts; benchmark answers are not loaded by the API.

Open [interactive API documentation](http://127.0.0.1:8000/docs) for request and
response schemas. Models and indexes load once during application startup.

| Route | Behavior |
| --- | --- |
| `GET /health` | Process liveness, 200 even when dependencies are unavailable. |
| `GET /ready` | Local corpus, index, tokenizer, and generation-adapter readiness; 503 with an unavailable-dependency code otherwise. |
| `GET /papers` | Paper IDs, titles, sections, and paragraph counts. |
| `GET /papers/{paper_id}/paragraphs/{paragraph_id}` | Original paragraph belonging to the specified paper; mismatched or missing pairs return 404. |
| `POST /questions` | JSON `paper_id` and `question`; returns the shared `AnswerResult` contract. |

Readiness checks local initialization and credentials, not the provider's current
network availability or quota. A subsequent provider failure is a question
request error, even if readiness returned 200.

Example:

```powershell
$body = @{ paper_id = '1911.07228'; question = 'What word embeddings were used?' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/questions -Method Post -ContentType application/json -Body $body
```

A successful answer contains claims and exact-span citation records. Fetch each
original paragraph and use the half-open Python character offsets `start_char`
and `end_char` to highlight the cited quote. These offsets count Unicode code
points, not JavaScript UTF-16 code units. Citation validity establishes a source
location; it does not establish that the model interpreted the passage correctly.

An insufficient-evidence response is HTTP 200 with status
`insufficient_evidence`, empty claims, and empty citations. Operational failures
are distinct:

| HTTP status | Meaning |
| --- | --- |
| 422 | Missing, blank, extra, or incorrectly typed fields; question longer than 2,000 characters; context-budget overflow. |
| 404 | Unknown paper or paragraph. |
| 502 | Rejected structured output/citation, or upstream HTTP failure. |
| 503 | Unavailable dependency, timeout, rate limit, or source/storage problem. |
| 500 | Unexpected internal failure, with a generic public message. |

Errors use `{"detail":{"code":"...","message":"...","request_id":"..."}}`.
Field-validation errors also include sanitized `errors` entries. Provider traces
and credentials are not returned. A numeric upstream `Retry-After` is forwarded
for throttling. The API does not automatically regenerate throttled answers.

Every response has an `X-Request-ID` header. Answer bodies, question-run JSON/
SQLite records, and API logs share that ID. Validation and readiness failures
have IDs too. Configure the `evidence_assistant.api` logger at INFO level to retain
route/status/request-ID logs. Question run logs contain question text and model
responses; keep them local and out of Git.

Deterministic tests use a real synthetic SQLite corpus and the shared core with
fake hosted responses. They are mechanics tests, not answer-quality evidence:

```powershell
python -m pytest tests/test_api.py -q
```

The real integration smoke is separate, uses one training-paper question, and
requires prepared artifacts and a provider key. It makes a live hosted request:

```powershell
$env:PAPERTRAIL_LIVE_API = '1'
python -m pytest tests/test_live_api.py -q
Remove-Item Env:PAPERTRAIL_LIVE_API
```

## Paper imports

PDF uploads and arXiv links use preview and explicit confirmation before adding a
paper. Imported paper IDs work with the existing question and paragraph routes.
See [the import API and limits](paper_import.md#http-endpoints).
