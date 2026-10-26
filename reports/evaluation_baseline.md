# Validation baseline

Date: 26 October 2026. Candidate: Groq `openai/gpt-oss-20b`, evidence-v1 prompt,
temperature 0 (provider behavior may vary), low reasoning effort, 512 output tokens,
1,536 evidence tokens, 4,096 context tokens, and a 256-token safety reserve.
Retrieval uses the pinned MiniLM encoder on CPU and the 4,440-chunk SQLite pilot.
No held-out test inference has been run.

## Selection and evidence eligibility

Counts below describe the saved pilot selections. Reasons can overlap and never
relabel a question unanswerable. Test metadata was counted without running retrieval
or inspecting test answer quality.

| Split | Questions | Strict text-only | Float evidence | Unmapped evidence | Answerable without positive evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train/debug | 19 | 18 | 1 | 0 | 0 |
| Validation | 92 | 72 | 11 | 6 | 3 |
| Test | 187 | 149 | 28 | 8 | 6 |

## Retrieval on all 92 validation questions

All methods use top five and the same shared generator-token budgeting policy;
metrics score the chunks actually supplied after whole-chunk trimming. Repeated
paragraph positions are alternatives, duplicate chunks earn no extra credit, and
references are scored individually without unioning annotator evidence.

| Method | Strict Hit@5 | Strict Recall@5 | Strict complete evidence | Positive-reference denominator |
| --- | ---: | ---: | ---: | ---: |
| BM25 | 43.94% (29/66) | 40.45% | 37.88% (25/66) | 66 |
| Dense | 54.55% (36/66) | 51.62% | 48.48% (32/66) | 66 |
| Hybrid | 56.06% (37/66) | 50.56% | 46.97% (31/66) | 66 |

The strict slice contains 72 questions; six lack a complete mapped positive
reference and are excluded from these retrieval denominators. On the whole
92-question selection, 71 have such a reference: BM25 Hit@5 is 30/71, dense 38/71,
and hybrid 39/71. These results establish no single winner: hybrid has more hits,
while dense retrieves more complete annotated evidence sets.

Detailed predictions, eligibility mappings, and manifest:
`reports/runs/validation-retrieval-v1/`. The report includes whole-set and strict
metrics with numerator, denominator, and exclusion counts.

## Hosted timing sample and larger batch

A three-question validation timing sample completed without service errors. All
three prompts matched calibrated provider input counts. Cold service loading was
6.96 seconds; warm end-to-end p50/p95 was 3.10/3.42 seconds. Actual usage totaled
3,720 input and 367 output tokens. This small, mixed-label sample is a runtime
smoke check, not a quality estimate.

The larger comparison uses the same deterministic 30 validation questions for
BM25, dense, and hybrid (90 requested cases), selected by SHA-256 of seed and
question ID before looking at answers. It retains all selected cases and flags;
strict-slice reporting is additional. Requests are paced; per-case checkpoints
and exact supplied passages are saved under
`reports/runs/validation-qa-baseline-30/`. Batch metrics and the manual source audit
will be recorded here after completion.

## Review boundary

[The audit rubric](../docs/evaluation.md) separates correctness, source support,
and refusal behavior. `validation_agent_audit.jsonl` contains explicitly labeled
agent source inspections. Human claim-support metrics remain unavailable until
a human reviewer labels the claims; structural citation validity is a separate
metric. A valid source span alone does not establish a correct answer.
