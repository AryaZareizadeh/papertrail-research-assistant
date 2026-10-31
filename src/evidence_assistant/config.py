"""Validated settings; loading configuration never downloads or creates files."""

from itertools import combinations
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_dir: Path = Path("data/raw")
    corpus_dir: Path = Path("data/corpus")
    evaluation_dir: Path = Path("data/evaluation")
    manifest_dir: Path = Path("data/manifests")
    artifact_dir: Path = Path("artifacts")
    report_dir: Path = Path("reports")
    library_dir: Path | None = None
    dotenv_path: Path = Path(".env")
    seed: int = 42
    retrieval_method: Literal["bm25", "dense", "hybrid"] = "hybrid"
    top_k: int = Field(default=5, gt=0)
    candidate_k: int = Field(default=20, gt=0)
    rrf_k: int = Field(default=60, gt=0)
    chunk_tokens: int = Field(default=192, gt=0)
    chunk_overlap_tokens: int = Field(default=32, ge=0)
    chunking_version: str = "paragraph-windows-v1"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_revision: str | None = None
    embedding_max_tokens: int = Field(default=256, gt=0)
    generation_model: str | None = None
    generation_digest: str | None = None
    generation_endpoint: str = "https://api.groq.com/openai/v1"
    generation_api_key_env: str = "GROQ_API_KEY"
    generation_tokenizer: str | None = None
    generation_tokenizer_revision: str | None = None
    generator_context_tokens: int = Field(default=4096, gt=0)
    max_evidence_tokens: int = Field(default=1536, gt=0)
    max_output_tokens: int = Field(default=512, gt=0)
    context_safety_margin_tokens: int = Field(default=256, ge=0)
    prompt_version: str = "evidence-v1"
    timeout_seconds: float = Field(default=60, gt=0)

    @model_validator(mode="after")
    def validate_relationships(self):
        if self.candidate_k < self.top_k:
            raise ValueError("candidate_k must be at least top_k")
        if self.chunk_overlap_tokens >= self.chunk_tokens:
            raise ValueError("chunk_overlap_tokens must be less than chunk_tokens")
        if self.chunk_tokens + 2 > self.embedding_max_tokens:
            raise ValueError("chunk_tokens must leave room for embedding special tokens")
        reserved = (
            self.max_evidence_tokens + self.max_output_tokens + self.context_safety_margin_tokens
        )
        if reserved >= self.generator_context_tokens:
            raise ValueError("context budget must leave room for instructions and question")
        if bool(self.generation_model) != bool(self.generation_tokenizer):
            raise ValueError(
                "generation_model and generation_tokenizer must be configured together"
            )
        path_fields = (
            "raw_dir",
            "corpus_dir",
            "evaluation_dir",
            "manifest_dir",
            "artifact_dir",
            "report_dir",
        )
        for left, right in combinations(path_fields, 2):
            a, b = getattr(self, left).resolve(), getattr(self, right).resolve()
            if a.is_relative_to(b) or b.is_relative_to(a):
                raise ValueError(f"{left} and {right} must not overlap")
        library = self.library_path.resolve()
        for name in path_fields:
            protected = getattr(self, name).resolve()
            if library.is_relative_to(protected) or protected.is_relative_to(library):
                raise ValueError(f"library_dir and {name} must not overlap")
        return self

    @property
    def database_path(self) -> Path:
        return self.artifact_dir / "corpus.sqlite"

    @property
    def library_path(self) -> Path:
        return self.library_dir or self.artifact_dir.parent / "library"


def load_config(path: Path) -> AppConfig:
    path = path.resolve()
    try:
        with path.open(encoding="utf-8") as handle:
            values = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc
    if values is None:
        values = {}
    if not isinstance(values, dict):
        raise ValueError("configuration must be a YAML mapping")
    for name, field in AppConfig.model_fields.items():
        if name.endswith("_dir") or name == "dotenv_path":
            raw = values.get(name, field.default)
            if raw is None:
                continue
            value = Path(raw).expanduser()
            values[name] = (path.parent / value).resolve()
    return AppConfig.model_validate(values)
