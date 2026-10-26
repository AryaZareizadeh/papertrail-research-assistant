# Implementation and experiment log

## 2026-10-26 — Initial implementation

Plan: `PaperTrail_Development_Guide.md`; binding specification: its Section 2.
The user approved implementing the guide, including SQLite first and PostgreSQL later.

### Pre-flight interfaces

| Tasks | Shared contract | Decision |
| --- | --- | --- |
| 1 → 2–10 | AppConfig and typed records | Pydantic records; all paths resolve against the config file. |
| 2 → 3, 6 | Corpus vs evaluation exports | Separate directories and consumers; stable positional IDs. |
| 3 → 4, 5 | Chunks and stored source offsets | Python half-open character offsets; original text preserved. |
| 4 → 5, 6 | RetrievedChunk and IndexManifest | Paper filtering before ranking; validate artifact compatibility. |
| 5 → 6, 8, 9 | AnswerResult and shared service | Separate abstentions from errors; citations built from storage. |
| 6 → 7, 10 | Frozen run manifests | Validation choices precede held-out test; report failed cases. |

Ruling: Initialize a new feature branch in this requested directory; no existing
repository/worktree exists to isolate. Cost if wrong: branch/directory relocation.

Ruling: The existing approved guide supplies both specification and task plan;
do not repeat design questions. Cost if wrong: later amendments to the guide.

Environment: Python 3.13.0 on Windows. `python -m venv` created the interpreter
but bundled `ensurepip` failed; use uv to install into the environment. Dependency
downloads require network access beyond the restricted shell sandbox.

### Task status

- Task 1: in progress — configuration tests written before implementation.
- Tasks 2–10: pending; no benchmark results or application readiness claimed.
