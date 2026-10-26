# Free hosted generation setup

The user selected hosted inference and requested a free service. The initial
provider is Groq Free Plan with model `openai/gpt-oss-20b`. Its strict JSON schema
support fits the structured claim/citation contract. Live generation and token
calibration passed with this user's account on 26 October 2026.

## Account and key

1. Create a free account at [Groq Console](https://console.groq.com/).
2. Keep it on the **Free Plan** and create an [API key](https://console.groq.com/keys).
3. Save the key locally in the project's ignored `.env` file:

   ```dotenv
   GROQ_API_KEY=your_key_here
   ```

   Alternatively, set the `GROQ_API_KEY` environment variable. Environment values
   take precedence over `.env`. The application does not upgrade an account or
   switch to a paid fallback.

4. Run setup and a small training-paper smoke test:

   ```powershell
   .\.venv\Scripts\python.exe -m evidence_assistant.cli prepare-generation-tokenizer
   .\.venv\Scripts\python.exe -m evidence_assistant.cli calibrate-generation
   .\.venv\Scripts\python.exe -m evidence_assistant.cli answer --paper-id 1911.07228 --question "What word embeddings were used?" --method hybrid
   ```

Only the tokenizer is downloaded for generation. Model inference runs at Groq;
MiniLM retrieval remains local. A missing key produces a model-service setup error.

## Free-tier limits

On 26 October 2026, the [official limits table](https://console.groq.com/docs/rate-limits)
listed 30 requests/minute, 1,000 requests/day, 8,000 tokens/minute, and 200,000
tokens/day for this model on the Free Plan. Account limits can differ; check the
console. The [billing documentation](https://console.groq.com/docs/billing-faqs)
separates the Free Plan from the paid Developer tier.

The token allowance can require spreading larger evaluation runs across days.
HTTP 429 remains a service error, never an insufficient-evidence answer. There is
no automatic model/provider fallback that would invalidate comparisons.

## Evidence and token accounting

The [Groq adapter](https://console.groq.com/docs/openai) requests non-streaming
[strict JSON schema output](https://console.groq.com/docs/structured-outputs).
Every returned claim must cite a supplied chunk; displayed quotes are reconstructed
from the original SQLite source span. This checks traceability, not semantic truth.

The pinned GPT-OSS tokenizer uses its native Harmony chat template, following
[official OpenAI documentation](https://developers.openai.com/cookbook/articles/gpt-oss/run-transformers).
The initial full-prompt count is explicitly an estimate because provider-added
schema/system formatting can differ. Runs retain estimated and actual provider
counts separately; unknown usage after a transport error is `null`, not zero.
The service rejects responses exceeding actual input/output limits.

The calibration command makes three training-paper probes and an independent
validation probe, without benchmark answers. The observed prompt offset was -11
tokens on all three probes; the fourth prompt matched at 908 tokens after applying
the offset. Loading the saved calibration reproduced that count. The signature
binds the endpoint, model, tokenizer files/revision, prompt, schema, and generation
options. Changed settings require recalibration. Each answer still records actual
usage and whether it matches the counter; a hosted backend can change over time.

A separate live smoke answered a training-paper question with traceable source
citations, and a calibration probe declined an unsupported marketing-budget
question. These are functional checks; benchmark answer quality remains for Task 6.

Groq remains the working baseline. After baseline evaluation, compare Requesty's
`nvidia/nemotron-3-ultra-550b-a55b` on identical questions and saved supplied passages.
Judge correctness, claim support, refusal/error behavior, and latency before
switching. Its provider format and token counter need their own live checks.

For the opt-in live integration test:

```powershell
$env:PAPERTRAIL_LIVE_GROQ = '1'
.\.venv\Scripts\python.exe -m pytest tests/test_live_generation.py -q
```

Ordinary tests use synthetic responses and make no provider calls. Run JSON and
the separate `reports/runs/runs.sqlite` database include source/configuration
provenance, safe error codes/stages, retries, and token usage. API keys and raw
provider error bodies are excluded.
