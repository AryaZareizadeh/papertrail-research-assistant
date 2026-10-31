# Imported-paper authorship retrieval — 31 October 2026

The saved question `who is the main author` on the imported GST paper returned
insufficient evidence. Its five dense hits came from pages 5–6; none included the
page-1 author block. The stored first-page text also contained literal small-cap
glyph labels such as `A/r.sc/y.sc/a.sc` in author names.

The library now enables a narrow authorship policy for imported documents. Identity
questions reserve the first two page-1 chunks before the remaining ranked hits.
Substantive questions about authors' methods retain normal retrieval. Base QASPER
indices leave this policy disabled. For these imported identity questions only,
the prompt includes a readable rendering of recognized single-letter `.sc` glyphs
alongside original evidence, plus guidance distinguishing first-listed and
corresponding authors from an unsupported inference about main contribution.

Stored sources, citation spans, vectors and existing answers are not rewritten.
Rendering aids count toward the evidence budget; the actual system prompt hash
and `pdf-authorship-v1` context policy are recorded for future answers.

## Verification

- Regression reproduced before the fix: first hit was Page 5 instead of Page 1.
- Rendering-aid budget regression also reproduced before its fix.
- Full offline suite: 195 passed, 2 opt-in hosted tests skipped. Ruff passed.
- Independent reviewer: no important issues; 9 authorship tests passed separately.
- Rebuilt and restarted local services without changing persistent papers.
- Replayed **local retrieval/context preparation only** for the original saved
  question. Hits now include pages 1, 1, 6, 6, 5. Both author names occur correctly
  in the supplied readable author block. Context estimate: 1,972 input tokens,
  including 1,532 evidence tokens within the 1,536-token evidence limit.
- Verified original request-file hash and imported source-database hash unchanged.
- No hosted answer-generation request or new benchmark run was made. The final
  model answer to the same question has not been rechecked.

Refresh the UI and submit a new question to use the new policy; saved answers do
not change retroactively. Re-importing the paper is unnecessary.
