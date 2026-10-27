# Local containers

Docker Desktop must be running with Linux containers. The image uses Python 3.13
and the tested dependency lock, with the CPU PyTorch wheel explicitly installed.
No GPU is required. First build downloads Python packages; application startup
uses only the prepared local model/tokenizer assets and contacts no model provider
until a question is submitted.

After the README's data/index/tokenizer preparation, export a separate runtime
bundle. This reads no benchmark answer files, changes no original artifacts, and
copies only the corpus, index, calibration, pinned encoder, and generation
tokenizer. It checks copied bytes and rewrites the two machine-specific snapshot
paths for the container. The calibration's signature and bytes remain unchanged.

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.runtime_export --output runtime/artifacts
docker compose up --build -d
```

The exporter refuses an existing destination. Use a fresh directory for a later
export and update the Compose mount if needed. `runtime/` is ignored by Git.

- API: http://127.0.0.1:8000/docs
- UI: http://127.0.0.1:8501
- Readiness: http://127.0.0.1:8000/ready

Compose reads the provider key from the ignored `.env` file at runtime. The UI
receives only `PAPERTRAIL_API_URL=http://api:8000`. No `.env`, dataset, benchmark
references, prepared weights, or private run logs are copied into the image.
The API mounts the exported artifacts read-only and a Docker-managed `runlogs`
volume as writable run storage. The image initializes its ownership for application
UID 10001, including on Linux hosts. Both services run as a non-root user with read-only root filesystems
and a writable temporary filesystem. Demo ports bind to localhost.

If ports are occupied, set `PAPERTRAIL_API_PORT` and `PAPERTRAIL_UI_PORT` before
running Compose; the internal service address remains `http://api:8000`.

```powershell
docker compose ps
docker compose logs --tail 50 api
docker compose down
```

Logs can contain questions and generated responses; keep them local. Stopping
Compose does not remove the exported bundle or run logs. Do not add `--volumes`
to `docker compose down` if you want to retain logs. To copy them to the host, use
`docker compose cp api:/runlogs ./reports/container`. Preserve `.env` locally.
The offline walkthrough in [demo instructions](demo.md) is separate and does not
require a provider key. New hosted integration inference is intentionally omitted
under the user's no-more-model-tests instruction; that limit must remain explicit
in the release report.
