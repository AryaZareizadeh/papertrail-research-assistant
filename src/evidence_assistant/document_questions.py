"""Narrow authorship intent and reversible PDF glyph rendering aids."""

import re

AUTHORSHIP_POLICY = "pdf-authorship-v1"
AUTHORSHIP_GUIDANCE = (
    " For authorship questions, distinguish the first-listed author from a corresponding "
    "author. Do not infer who made the main contribution from author order. If 'main author' "
    "is ambiguous, report the supported first-listed/corresponding roles with that caveat. "
    "An optional readable_text field only decodes PDF small-cap glyph names in the original "
    "cited text; retain the original chunk ID as its citation."
)


def is_authorship_question(question: str) -> bool:
    normalized = " ".join(re.sub(r"[^\w\s-]", "", question.casefold()).split())
    suffix = r"(?: (?:of|for|on) (?:this|the) (?:paper|article|study))?"
    role = r"(?:(?:first|main|lead|corresponding|senior|last|co) )?"
    patterns = [
        r"who (?:is|are) (?:the )?" + role + r"authors?" + suffix,
        r"(?:please )?(?:list|name|identify|show)(?: me)? (?:all )?(?:the )?authors?" + suffix,
        r"who (?:wrote|authored) (?:this|the) (?:paper|article|study)",
        role + r"authors?(?: names?)?" + suffix,
    ]
    return any(re.fullmatch(pattern, normalized) for pattern in patterns)


def readable_pdf_text(text: str) -> str:
    """Decode literal single-letter small-cap glyph labels; never rewrite stored spans."""
    decoded = re.sub(r"/([A-Za-z])\.sc(?![a-z])", r"\1", text)
    if decoded != text:
        decoded = re.sub(r"(?<=[a-z])AND\s*(?=[A-Z])", " AND ", decoded)
    return decoded
