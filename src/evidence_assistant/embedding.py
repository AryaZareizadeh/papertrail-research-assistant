"""Explicit embedding-model acquisition followed by local-only loading."""

import json
from pathlib import Path

from evidence_assistant.config import AppConfig
from evidence_assistant.data import write_json


def _prepare(config: AppConfig, *, weights: bool) -> dict:
    from huggingface_hub import snapshot_download

    snapshot = snapshot_download(
        config.embedding_model,
        revision=config.embedding_revision,
        cache_dir=config.artifact_dir.parent / ".cache" / "huggingface",
        ignore_patterns=["onnx/*", "openvino/*", "*.h5", "*.ot", "pytorch_model.bin"],
        allow_patterns=None
        if weights
        else [
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "vocab.txt",
            "sentence_bert_config.json",
            "config.json",
            "modules.json",
            "config_sentence_transformers.json",
            "1_Pooling/config.json",
        ],
    )
    tokenizer = TokenizerAdapter(Path(snapshot))
    metadata = {
        "model": config.embedding_model,
        "revision": Path(snapshot).name,
        "snapshot": str(Path(snapshot).resolve()),
        "effective_max_tokens": tokenizer.model_max_length,
        "weights_available": (Path(snapshot) / "model.safetensors").is_file(),
    }
    write_json(config.artifact_dir / "embedding_model.json", metadata)
    return metadata


def prepare_embedding(config: AppConfig) -> dict:
    return _prepare(config, weights=True)


def prepare_tokenizer(config: AppConfig) -> dict:
    return _prepare(config, weights=False)


class TokenizerAdapter:
    """Use the model's native fast tokenizer without importing the generation/torch stack."""

    def __init__(self, snapshot: Path):
        from tokenizers import Tokenizer

        self.native = Tokenizer.from_file(str(snapshot / "tokenizer.json"))
        self.native.no_truncation()
        self.native.no_padding()
        tokenizer_config = json.loads((snapshot / "tokenizer_config.json").read_text("utf-8"))
        sentence_config = json.loads((snapshot / "sentence_bert_config.json").read_text("utf-8"))
        self.model_max_length = min(
            tokenizer_config["model_max_length"], sentence_config["max_seq_length"]
        )

    def __call__(self, text, *, add_special_tokens=True, return_offsets_mapping=False, **kwargs):
        encoding = self.native.encode(text, add_special_tokens=add_special_tokens)
        result = {"input_ids": encoding.ids}
        if return_offsets_mapping:
            result["offset_mapping"] = encoding.offsets
        return result


def embedding_metadata(config: AppConfig) -> dict:
    path = config.artifact_dir / "embedding_model.json"
    if not path.is_file():
        raise ValueError("Run prepare-tokenizer before chunking; prepare-embedding before indexing")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if metadata["model"] != config.embedding_model or (
        config.embedding_revision and config.embedding_revision != metadata["revision"]
    ):
        raise ValueError("Prepared embedding model differs from configuration; prepare it again")
    return metadata


def load_tokenizer(config: AppConfig):
    return TokenizerAdapter(Path(embedding_metadata(config)["snapshot"]))


def load_encoder(config: AppConfig):
    metadata = embedding_metadata(config)
    if not metadata.get("weights_available", False):
        raise ValueError(
            "Run prepare-embedding and install model dependencies before dense indexing"
        )
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(metadata["snapshot"], device="cpu", local_files_only=True)
