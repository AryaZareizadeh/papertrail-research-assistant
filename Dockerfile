FROM python:3.13-slim@sha256:8d9d0b8bcf6506481eae4907c18f5e3e7902e629f5f6d684f9e7c32e85e3ddf0

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
    HF_HOME=/tmp/huggingface XDG_CACHE_HOME=/tmp/cache
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.lock.txt ./
# Install the CPU wheel explicitly; the remaining tested lock is installed without
# resolving platform-specific CUDA dependencies from the default torch wheel.
RUN python -m pip install --no-deps --index-url https://download.pytorch.org/whl/cpu torch==2.14.1 \
    && python -m pip install --no-deps -r requirements.lock.txt
COPY pyproject.toml README.md LICENSE NOTICE ./
COPY src ./src
COPY tools ./tools
COPY examples ./examples
COPY .streamlit ./.streamlit
COPY config.docker.yaml ./config.docker.yaml
COPY docs/data_card.md docs/model_card.md ./docs/
RUN python -m pip install --no-deps --no-build-isolation . && python -m pip check \
    && useradd --create-home --uid 10001 papertrail \
    && mkdir /runlogs /library && chown papertrail:papertrail /runlogs /library
USER papertrail
EXPOSE 8000 8501
CMD ["python", "-m", "uvicorn", "evidence_assistant.api:app", "--host", "0.0.0.0", "--port", "8000"]
