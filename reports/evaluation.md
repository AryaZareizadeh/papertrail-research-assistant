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

## Completed held-out pilot

The final configuration was frozen before held-out inference at code `7788140`.
Frozen-manifest SHA-256:
`878815f1e6e4d922661b3e2932f795db4d4a7f23512d5dc27bc462b01c47eeba`.
All **187/187 questions from the deterministic 50-paper test pilot** have now been
attempted. After the original stop at 154 attempts, the user explicitly requested
completion on 27 October 2026. Only the 33 unattempted questions were added.
All original 154 prediction records remain byte-for-byte intact, including the
two HTTP 429 failures. There are 185 completed model responses and 2
retained failed cases, with zero unattempted questions. No failed case was retried.

| Metric | All 187 selected questions | Strict text-only: 149 questions |
| --- | ---: | ---: |
| Official Answer F1 | 0.2600 | 0.2938 |
| Official Evidence F1 | 0.4374 | 0.4928 |
| Answer coverage | 116/187 (62.03%) | 100/149 (67.11%) |
| Structurally valid citations | 178/178 (100.00%) | 154/154 (100.00%) |
| False refusals on consensus-answerable questions | 54/162 (33.33%) | 34/126 (26.98%) |
| Abstention precision on consensus-labeled refusals | 3/57 (5.26%) | 3/37 (8.11%) |
| Unanswerable recall | 3/4 (75.00%) | 3/4 (75.00%) |
| System errors | 2/187 (1.07%) | 2/149 (1.34%) |
| Unattempted questions | 0/187 (0.00%) | 0/149 (0.00%) |
| Warm end-to-end p50 / p95 | 1.31 / 2.65 s | 1.29 / 2.65 s |


Answer F1 is lexical overlap, not accuracy. Official scoring omits the provider
errors from its prediction adapter and assigns them zero; its "Missing predictions"
count therefore includes retained service failures, while product missing-case
counts above are zero. All 187 selected questions stay in whole-set denominators.
The strict slice contains 126 consensus-answerable, four consensus-unanswerable,
and 19 mixed-annotation questions; the whole set contains 162, four, and 21.
Structural citation validity does not establish semantic claim support, which
remains unavailable without human review.

Known usage is 181,986 input plus 18,915 output tokens
(200,901 total); usage for the two historical throttles
remains unknown. All 185 non-error responses match the
frozen token calibration. Initialization and 20-second pacing are excluded from
warm request latency. The run resumed later on the same day; hosted weights are
not locally pinnable, so model IDs and returned fingerprints remain recorded.

The original frozen evaluator was loaded from a byte-verified copy to exclude
later API/UI/export modules. Configuration, selection, data, model artifacts,
prompt, scoring identity, original checkpoint binding, and consumed-selection
marker are unchanged. No held-out outcome was used to tune settings.

See [held-out completion and provenance](heldout_status.md) and the
[sanitized machine-readable summary](heldout_summary.json). The private original
predictions/checkpoint remain in `reports/runs/final-test/`.

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
`nemotron-fixed-context-30`, and completed `final-test`. Explicit v3 rescoring
preserved every method metric without new generation. Original reports remain
intact. Windows / Python 3.13.0; 16.8 GB RAM; retrieval on CPU. Baseline process
peak working set was about 736 MiB. Warm latency includes retrieval, provider,
and validation; initialization and deliberate pacing are separate.

Public-benchmark contamination, incomplete annotations, agent-review bias, hosted
model variation, the small pilot, and retained provider failures limit conclusions.
