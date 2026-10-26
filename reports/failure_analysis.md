# Task 7: controlled generation-backend experiment

The Groq baseline is preserved. Full results and the accepted, explicitly labeled
agent audit are in evaluation_baseline.md and validation_agent_audit.jsonl.
Human support scores remain unavailable.

## Baseline diagnosis

Retrieval misses and partial evidence remain common: hybrid has complete annotated
text evidence for 31/66 strict eligible questions on the 92-question pilot. The
30-question generation sample also exposes wrong interpretation (cognitive versus
stylistic features; unsupported best-system ranking), partially attributed details,
over-refusal despite usable context, incomplete responses, and one disallowed
citation. Table-dependent cases and answerability disagreements are reported,
not silently treated as retrieval or model failures. No ingestion/chunk-span
corruption was found in the verified pilot.

## Hypothesis and controls, registered before candidate inference

The user's requested experiment changes the hosted generation backend from Groq
GPT-OSS-20B to Requesty's exact free NVIDIA Nemotron Ultra route. Hypothesis:
Nemotron will distinguish the requested concepts and source-supported negative
answers more reliably, improving correct supported responses on fixed context.
It cannot repair a retrieval miss when the required passage was never supplied.

Use all 30 original hybrid questions, in the same saved order, with exactly the
saved supplied chunks/text. Keep source hashes, common evidence-only instructions,
claim/citation schema, 1,536 evidence-token cap, 4,096 context limit, 512 output
tokens, and 256-token reserve. Reject a comparison case rather than silently
changing its passages to fit. Record each backend's tokenizer and actual usage.

Requesty catalog preflight succeeded with the saved key. Exact route
`nvidia/nemotron-3-ultra-550b-a55b` has zero input/output price and no configured
fallback. Catalog flags both output JSON modes unsupported, despite generic docs
describing JSON mode. The candidate will receive the same schema information as
a prompt formatting instruction and use the same local validation. This required
transport/format adaptation makes this a backend comparison, not a claim of pure
model-only isolation. Any malformed output remains a failed case. Verify format
and pinned tokenizer accounting on training questions before validation inference.

## Provisional decision rule

Keep Groq unless the candidate produces at least two additional fully correct
answers on the 30 cases, does not increase unsupported-claim rate or false refusals,
correctly refuses at least one of the two consensus-unanswerable questions, and
has no more service/format errors than the baseline (one). Require warm p95 at or
below 15 seconds for an interactive question. These are declared engineering gates
for a small pilot, not statistical significance thresholds. Compare source support
using the same accepted agent rubric and retain all judgments for later human review.

No result is available yet. No active configuration has been switched. Final
candidate freezing and held-out evaluation follow the validation decision.

## Training-only integration checks

Candidate catalog access succeeded using the saved key; no key values were logged.
The initial native thinking-disable flag still produced reasoning and a truncated
512-token training response. A controlled two-call diagnostic showed that adding
Requesty's documented reasoning_effort=none suppressed reasoning. This setting was
chosen on training probes, before any candidate validation inference.

Three successful training probes and an independent fourth all matched their
pinned native tokenizer counts at offset zero. The fourth count was 1,314 tokens,
also reproduced after loading persisted calibration. All four reported zero cost.
A rate-limit response during an earlier attempt remains recorded. Calibration can
resume compatible probes, and --fresh handles backend token-format drift.

Independent code review found two P2 issues: nonzero usage cost on rejected output
did not stop dispatch, and interruption between prediction and manifest writes
could prevent resume. Both were reproduced by failing tests and fixed in one pass.
A single atomic checkpoint now precedes its derived prediction/manifest exports.
The full suite passes 116 tests with one opt-in live test skipped. Validation
comparison remains unrun at this checkpoint; Groq is unchanged.
