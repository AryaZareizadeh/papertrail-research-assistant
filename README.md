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
all 80 dependency versions matched, dependency checks passed, and all 48 tests passed.

Configuration paths resolve relative to the YAML file, rather than the current
working directory. `doctor` inspects local files and package metadata without
downloading data or models. Missing artifacts are expected before setup.

Storage starts with SQLite. A later version will migrate to PostgreSQL while
preserving document identifiers and citation source spans.

See [the experiment log](reports/experiment_log.md) for verified progress and
remaining work. No answer-quality or runtime claims have been measured yet.

## Current working milestone

The implemented commands cover configuration, official QASPER download and
normalization, tokenizer preparation, source-preserving SQLite chunks, and BM25
retrieval. Real dense and hybrid retrieval now work with the pinned MiniLM model;
the pilot index contains 4,440 normalized 384-dimensional vectors. Answer generation,
evaluation, API, UI, and Docker packaging are still pending.

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

