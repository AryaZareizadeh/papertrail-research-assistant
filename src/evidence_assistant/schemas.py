"""Shared contracts. Benchmark references are never runtime document fields."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from evidence_assistant.config import AppConfig as AppConfig

Split = Literal["train", "validation", "test", "user"]
Method = Literal["bm25", "dense", "hybrid"]
Status = Literal["answered", "insufficient_evidence"]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Paper(Record):
    paper_id: str
    split: Split
    title: str
    abstract: str
    source_revision: str


class Paragraph(Record):
    paragraph_id: str
    paper_id: str
    section_index: int
    section_name: str
    paragraph_index: int
    text: str
    text_sha256: str


class Chunk(Record):
    chunk_id: str
    paragraph_id: str
    paper_id: str
    section_name: str
    start_char: int = Field(ge=0)
    end_char: int = Field(gt=0)
    text: str
    token_count: int = Field(gt=0)
    chunking_version: str

    @model_validator(mode="after")
    def validate_span(self):
        if self.end_char <= self.start_char or len(self.text) != self.end_char - self.start_char:
            raise ValueError("chunk text length must match its half-open source span")
        return self


class RetrievedChunk(Record):
    chunk: Chunk
    rank: int = Field(gt=0)
    score: float
    method: Method


class AnswerReference(Record):
    annotation_id: str
    answer_type: str
    answer_text: str
    unanswerable: bool
    evidence: list[str]
    highlighted_evidence: list[str]
    raw_answer: dict[str, Any] = Field(default_factory=dict)


class GoldQuestion(Record):
    question_id: str
    paper_id: str
    question: str
    references: list[AnswerReference]
    annotation_disagreement: bool
    evidence_mapping_status: str = "pending"
    uses_float_evidence: bool


class DraftClaim(Record):
    text: str = Field(min_length=1)
    citation_chunk_ids: list[str] = Field(min_length=1)


class DraftAnswer(Record):
    status: Status
    claims: list[DraftClaim]

    @model_validator(mode="after")
    def validate_claims(self):
        if (self.status == "answered") != bool(self.claims):
            raise ValueError(
                "answered requires claims; insufficient_evidence requires empty claims"
            )
        return self


class Citation(Record):
    chunk_id: str
    paper_id: str
    paragraph_id: str
    section_name: str
    start_char: int
    end_char: int
    quote: str


class AnswerResult(Record):
    request_id: str
    paper_id: str
    status: Status
    claims: list[DraftClaim]
    citations: list[Citation]
    retrieved_chunk_ids: list[str]
    method: Method
    model_id: str
    prompt_version: str
    index_version: str
    latency_ms: float


class DataManifest(Record):
    dataset_version: str = "qasper-v0.3"
    source_urls: list[str] = Field(default_factory=list)
    file_hashes: dict[str, str] = Field(default_factory=dict)
    observed_split_counts: dict[str, dict[str, int]] = Field(default_factory=dict)
    selection_seed: int = 42
    selection_rule: str = "sha256(seed + split + paper_id), ascending"
    selected_paper_ids: dict[str, list[str]] = Field(default_factory=dict)
    normalization_version: str = "qasper-document-only-v1"


class IndexManifest(Record):
    vector_file: str = "embeddings.npy"
    corpus_hash: str
    chunking_hash: str
    embedding_model: str
    embedding_revision: str
    tokenizer_settings: dict[str, Any]
    vector_dimension: int
    ordered_chunk_ids: list[str]
    artifact_hashes: dict[str, str]
    index_version: str


class EvidenceItem(Record):
    original: str
    candidate_paragraph_ids: list[str]
    match_method: str
    status: Literal["exact", "whitespace", "float", "unmapped"]


class AnnotationMapping(Record):
    annotation_id: str
    items: list[EvidenceItem]


class EvidenceMapping(Record):
    question_id: str
    annotations: list[AnnotationMapping]


class MetricValue(Record):
    value: float | None
    numerator: float
    denominator: int
    excluded_counts: dict[str, int] = Field(default_factory=dict)


class RetrievalMetrics(Record):
    metrics: dict[str, MetricValue]
    split: str
    slice: str
    run_id: str
    policy_hash: str
    config_hash: str


class AnswerMetrics(RetrievalMetrics):
    pass
