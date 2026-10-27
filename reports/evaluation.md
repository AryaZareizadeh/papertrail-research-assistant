# Evaluation and final configuration

## Selected configuration

The user selected Groq `openai/gpt-oss-20b` on 27 October 2026. Use dense retrieval
with the pinned MiniLM encoder, top five chunks, evidence-v1 prompt, 1,536 evidence
tokens, 512 output tokens, 4,096 total context tokens, and 256 tokens of reserve.
SQLite remains the version-one store; PostgreSQL is a later migration.

## Completed validation

All 92 validation-pilot questions were used for retrieval comparison. A
deterministic 30-question slice was used for the three Groq generation baselines
and the fixed-context Requesty/Nemotron comparison. These are pilot results, not
full-benchmark scores. Answer F1 measures lexical overlap, not accuracy.

| Validation configuration | Questions | Answer F1 | Errors | Warm p95 |
| --- | ---: | ---: | ---: | ---: |
| Groq / BM25 | 30 | 0.3285 | 0/30 | 4.26 s |
| Groq / dense | 30 | 0.3917 | 0/30 | 2.93 s |
| Groq / hybrid | 30 | 0.3417 | 1/30 | 2.40 s |
| Requesty Nemotron Ultra / identical saved hybrid context | 30 | 0.3818 | 5/30 | 5.93 s |

Dense retrieval covered a complete annotated evidence set on 32/66 strict eligible
questions, versus 31/66 for hybrid; its recall was 0.5162 versus 0.5056. Dense had
one more false refusal in the generation slice (6/23 versus 5/23). The choice is
provisional evidence from a small pilot, not statistical superiority.

Nemotron improved substantive answer correctness in the accepted agent audit
(12 versus 11), but five throttled cases failed the declared operational gate.
Its provider-specific formatting and reasoning settings differed; this is a
backend comparison. No unsupported claim rate is inferred from structural
citation validity. Human claim-support measurements remain unavailable.

See [validation baseline](evaluation_baseline.md), [failure analysis](failure_analysis.md),
[model comparison](model_comparison.md), and [scoring protocol](../docs/evaluation.md)
for eligibility exclusions, reference handling, annotation disagreements, usage,
hardware, audit rubric, and all measured tradeoffs.

## Incomplete held-out pilot

The final configuration was frozen before held-out inference at code `7788140`.
Frozen-manifest SHA-256:
`878815f1e6e4d922661b3e2932f795db4d4a7f23512d5dc27bc462b01c47eeba`.
The pilot selected 50 test papers and all 187 questions. The user stopped further
model tests after 154 attempts: 152 model responses, two retained HTTP 429 errors,
and 33 unattempted questions. No completed 187-question test score is claimed.
Known usage was 149,067 input and 15,712 output tokens; failed-call usage is unknown.
Partial run metrics are preserved locally but are not presented as a completed
held-out result or used to choose settings.

The remaining inference requirement was explicitly waived by the user. Preserve
the checkpoint and consumed-selection marker; do not resume unless asked. The
frozen manifest describes its original code, not later API/UI/packaging additions.
This closes Task 7 with a declared deviation rather than claiming its full
held-out acceptance check passed. See [held-out status](heldout_status.md).

## Reproducibility and limits

QASPER v0.3 pilot: 5 training papers / 19 questions, 30 validation papers / 92
questions, 50 test papers / 187 questions. Runtime corpus: 85 papers, 4,043 original
paragraphs, 4,440 source-preserving chunks and normalized 384-dimensional vectors.
Benchmark references are separate from runtime documents.

Encoder: `sentence-transformers/all-MiniLM-L6-v2`, revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Generation tokenizer:
`openai/gpt-oss-20b`, revision `6cee5e81ee83917806bbde320786a8fb61efebee`.
Groq token calibration offset: -11, independently checked against a fourth prompt.
Hosted weights cannot be pinned locally; requested IDs and returned fingerprints
are recorded. The freeze binds actual local model, tokenizer, vector, corpus,
prompt, selection, code, scoring policy, and dependency-lock hashes.

Local run IDs: `validation-qa-baseline-30`, `validation-retrieval-baseline`,
`nemotron-fixed-context-30`, and incomplete `final-test`. Explicit v3 rescoring
preserved every method metric without new generation. Original reports remain
intact. Windows / Python 3.13.0; 16.8 GB RAM; retrieval on CPU. Baseline process
peak working set was about 736 MiB. Warm latency includes retrieval, provider,
and validation; initialization and deliberate pacing are separate.

Public-benchmark contamination, incomplete annotations, agent-review bias, hosted
model variation, the small pilot, and the incomplete held-out run limit conclusions.
