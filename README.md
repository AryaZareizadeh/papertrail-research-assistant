# PaperTrail

A research-paper assistant that answers questions about one selected paper and
links its claims to exact source passages. Implementation follows
[the development guide](PaperTrail_Development_Guide.md).

## Development

Python 3.11 or newer is required. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe -m evidence_assistant.cli --help
.\.venv\Scripts\python.exe -m evidence_assistant.cli doctor
.\.venv\Scripts\python.exe -m pytest -q
```

If Python's bundled `ensurepip` is unavailable, create the environment with
`uv venv .venv` and install with:

```powershell
uv pip install --python .venv\Scripts\python.exe -r requirements.lock.txt
uv pip install --python .venv\Scripts\python.exe --no-deps --no-build-isolation -e .
```

The full lock was reproduced in a fresh environment on Windows / Python 3.13.0;
the dependency versions matched and dependency checks passed. The updated full
lock contains 81 dependency pins; 117 tests pass and one opt-in live test is skipped.

Configuration paths resolve relative to the YAML file, rather than the current
working directory. `doctor` inspects local files and package metadata without
downloading data or models. Missing artifacts are expected before setup.

Storage starts with SQLite. A later version will migrate to PostgreSQL while
preserving document identifiers and citation source spans.

See [the experiment log](reports/experiment_log.md) for verified progress and
remaining work. Validation retrieval and answer-quality measurements are recorded;
the final held-out pilot was stopped at the user's request and remains incomplete.

## Current working milestone

The implemented commands cover configuration, official QASPER download and
normalization, tokenizer preparation, source-preserving SQLite chunks, and BM25
retrieval. Real dense and hybrid retrieval now work with the pinned MiniLM model;
the pilot index contains 4,440 normalized 384-dimensional vectors. Hosted answer
generation and citation validation passed synthetic-provider tests and a live Groq
smoke test. A pinned tokenizer was calibrated against four provider prompts.
The evaluator compared retrieval on 92 validation questions and hosted answers on
the same 30 questions across three methods. See the
[baseline report](reports/evaluation_baseline.md) and
[evaluation commands](docs/evaluation.md). The 30-response agent audit is complete;
the user accepted it for Task 6. Human claim-support scores remain unavailable.
The [model comparison](reports/model_comparison.md) is complete: Groq remains active,
and dense is the selected retrieval baseline. Task 7's once-only held-out test is
stopped at the user's request after 154/187 attempts;
see [held-out progress](reports/heldout_status.md). A reviewed FastAPI draft is saved
separately on `codex/api-draft`; integration waits for that test to finish. UI and
Docker packaging are pending.

The complete dependency installation now works. For a smaller SQLite/BM25-only
environment, the original bootstrap lock remains available:

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.bootstrap.lock.txt
uv pip install --python .venv\Scripts\python.exe --no-deps --no-build-isolation -e .
```

`requirements.bootstrap.lock.txt` covers only the SQLite/BM25 milestone. Use
`requirements.lock.txt` for the full dependency set. A bootstrap install intentionally
does not satisfy every dependency in `pyproject.toml`.

Prepare the data and run keyword retrieval:

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli download
.\.venv\Scripts\python.exe -m evidence_assistant.cli normalize
.\.venv\Scripts\python.exe -m evidence_assistant.cli prepare-tokenizer
.\.venv\Scripts\python.exe -m evidence_assistant.cli chunk
.\.venv\Scripts\python.exe -m evidence_assistant.cli retrieve --paper-id 1911.07228 --question "What word embeddings were used?" --method bm25
```

`chunk` uses the saved 85-paper pilot by default; `--all-papers` explicitly expands
it. Only `download`, `prepare-tokenizer`, and `prepare-embedding` acquire remote
artifacts. Other commands load local files. Before dense/hybrid retrieval, finish
the full dependency install, run `prepare-embedding`, then `index`. Vector files
use content-addressed names and a published manifest so a failed new index cannot
overwrite the previous working vectors.

See [training retrieval observations](reports/training_retrieval_notes.md) for
successes and misses. A retrieval result is evidence to inspect, not a generated
answer or a correctness guarantee.

## Hosted answer generation

Use [the free hosted-model setup guide](docs/hosted_model_setup.md). The configured
candidate is Groq Free Plan with `openai/gpt-oss-20b`; put its key in the ignored
`.env` file as `GROQ_API_KEY`. Generation model weights are not downloaded.

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli prepare-generation-tokenizer
.\.venv\Scripts\python.exe -m evidence_assistant.cli calibrate-generation
.\.venv\Scripts\python.exe -m evidence_assistant.cli answer --paper-id 1911.07228 --question "What word embeddings were used?" --method hybrid
```

Task 5 is verified for the Groq baseline. Regular tests make no provider calls.
Calibration makes four hosted requests and must be repeated if its bound settings
change. Mutable run records are stored separately
from the corpus in `reports/runs/runs.sqlite` and per-question JSON files.

