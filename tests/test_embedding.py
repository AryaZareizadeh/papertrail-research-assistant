import json

import pytest

from evidence_assistant.config import AppConfig
from evidence_assistant.embedding import embedding_metadata, load_tokenizer


def test_local_tokenizer_respects_sentence_transformer_limit_and_offsets(tmp_path):
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace

    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    native = Tokenizer(WordLevel({"[UNK]": 0, "hello": 1, "world": 2}, unk_token="[UNK]"))
    native.pre_tokenizer = Whitespace()
    native.enable_truncation(max_length=1)
    native.save(str(snapshot / "tokenizer.json"))
    (snapshot / "tokenizer_config.json").write_text(json.dumps({"model_max_length": 512}))
    (snapshot / "sentence_bert_config.json").write_text(json.dumps({"max_seq_length": 10}))
    config = AppConfig(artifact_dir=tmp_path / "artifacts")
    config.artifact_dir.mkdir()
    (config.artifact_dir / "embedding_model.json").write_text(
        json.dumps(
            {
                "model": config.embedding_model,
                "revision": "synthetic",
                "snapshot": str(snapshot),
                "effective_max_tokens": 10,
            }
        )
    )
    tokenizer = load_tokenizer(config)
    assert tokenizer.model_max_length == 10
    result = tokenizer("hello world", add_special_tokens=False, return_offsets_mapping=True)
    assert len(result["input_ids"]) == 2
    assert result["offset_mapping"] == [(0, 5), (6, 11)]


def test_mismatched_prepared_revision_is_rejected(tmp_path):
    config = AppConfig(artifact_dir=tmp_path / "artifacts", embedding_revision="wanted")
    config.artifact_dir.mkdir()
    (config.artifact_dir / "embedding_model.json").write_text(
        json.dumps(
            {
                "model": config.embedding_model,
                "revision": "different",
                "snapshot": ".",
            }
        )
    )
    with pytest.raises(ValueError, match="differs"):
        embedding_metadata(config)
