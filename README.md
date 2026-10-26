# PaperTrail

A research-paper assistant that answers questions about one selected paper and
links its claims to exact source passages. Implementation follows
[the development guide](PaperTrail_Development_Guide.md).

## Development

Python 3.11 or newer is required. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m evidence_assistant.cli --help
.\.venv\Scripts\python.exe -m evidence_assistant.cli doctor
.\.venv\Scripts\python.exe -m pytest -q
```

If Python's bundled `ensurepip` is unavailable, create the environment with
`uv venv .venv` and install using `uv pip install --python .venv\Scripts\python.exe -e ".[dev]"`.

Configuration paths resolve relative to the YAML file, rather than the current
working directory. `doctor` inspects local files and package metadata without
downloading data or models. Missing artifacts are expected before setup.

Storage starts with SQLite. A later version will migrate to PostgreSQL while
preserving document identifiers and citation source spans.

See [the experiment log](reports/experiment_log.md) for verified progress and
remaining work. No answer-quality or runtime claims have been measured yet.

