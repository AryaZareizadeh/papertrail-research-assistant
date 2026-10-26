import pytest

from evidence_assistant.generation_tokens import GenerationCounter


class TemplateTokenizer:
    def encode(self, text, *, add_special_tokens=False):
        return text.split()

    def apply_chat_template(self, messages, **kwargs):
        assert kwargs["add_generation_prompt"] is True
        assert kwargs["tokenize"] is True
        assert kwargs["return_dict"] is False
        return [0] * (10 + sum(len(m["content"].split()) for m in messages))


def test_counter_accounts_for_chat_template_and_schema():
    counter = GenerationCounter(TemplateTokenizer(), identity="synthetic")
    assert counter.count_text("one two three") == 3
    assert counter.count_prompt([{"role": "user", "content": "one two"}], {"type": "object"}) > 12


def test_counter_applies_calibrated_provider_overhead():
    messages, schema = [{"role": "user", "content": "one two"}], {"type": "object"}
    baseline = GenerationCounter(TemplateTokenizer(), identity="synthetic")
    calibrated = GenerationCounter(TemplateTokenizer(), identity="synthetic", prompt_offset=-3)
    assert calibrated.count_prompt(messages, schema) == baseline.count_prompt(messages, schema) - 3


def test_calibration_rejects_inconsistent_provider_counts():
    from evidence_assistant.generation_tokens import infer_prompt_offset

    assert (
        infer_prompt_offset(
            [
                {"estimated": 100, "actual": 89},
                {"estimated": 200, "actual": 189},
                {"estimated": 300, "actual": 289},
            ]
        )
        == -11
    )
    with pytest.raises(ValueError, match="consistent"):
        infer_prompt_offset(
            [
                {"estimated": 100, "actual": 89},
                {"estimated": 200, "actual": 190},
                {"estimated": 300, "actual": 289},
            ]
        )
