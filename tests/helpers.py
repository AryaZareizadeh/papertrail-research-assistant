import re


class OffsetTokenizer:
    """Synthetic tokenizer for offline offset/limit tests; not a model-quality substitute."""

    model_max_length = 256

    def __call__(self, text, *, add_special_tokens=True, return_offsets_mapping=False, **kwargs):
        spans = [(match.start(), match.end()) for match in re.finditer(r"\S+", text)]
        result = {"input_ids": list(range(len(spans) + (2 if add_special_tokens else 0)))}
        if return_offsets_mapping:
            result["offset_mapping"] = spans
        return result
