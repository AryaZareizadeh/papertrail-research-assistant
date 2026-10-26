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
`reports/runs/validation-qa-baseline-30/`. All 90 cases completed; all 90 actual
input counts matched the calibrated counter. No context needed trimming in this
sample (maximum evidence count 1,035 tokens); synthetic tests cover whole-chunk
budget trimming. Generation behavior is pinned to code checkpoint `0e420e4`.

| Method | Whole-set Answer F1 | Strict Answer F1 (25 cases) | Answer coverage | False refusals / 23 answerable | Errors / 30 | Warm p50 / p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BM25 | 0.3285 | 0.3505 | 19/30 | 7/23 | 0/30 | 1.27 / 4.26 s |
| Dense | 0.3917 | 0.4273 | 20/30 | 6/23 | 0/30 | 1.51 / 2.93 s |
| Hybrid | 0.3417 | 0.3667 | 20/30 | 5/23 | 1/30 | 1.41 / 2.40 s |

Answer F1 is lexical overlap, not an accuracy percentage. Boolean references are
especially sensitive to the verbose claim format: a semantically correct full
sentence may not contain the literal token Yes or No. Keep the official score
unchanged and interpret it alongside source inspection.

There are 23 consensus-answerable, two consensus-unanswerable, and five mixed
questions. All three methods answered both consensus-unanswerable questions, so
unanswerable recall is **0/2**. Abstention precision is **0/7, 0/6, and 0/5** for
BM25, dense, and hybrid respectively on consensus-labeled questions. The sample
is small, but it exposes a real need to improve semantic distinctions and refusals.

Displayed citations passed source validation: BM25 24/24, dense 26/26, hybrid 28/28.
One hybrid draft was rejected with `citation_not_supplied`; it remains an error
and receives official Answer F1 zero. It is not a successful refusal or a valid
displayed citation. Structural validity does not establish claim support.

The 90 cases used 94,563 actual input and 9,037 output tokens (103,600 total),
with no unknown counts. Cold service loading in this run was 13.05 seconds. Peak
Windows process working set was 772,030,464 bytes (about 736 MiB), including imports
and local retrieval/tokenization; generation ran at Groq. These are single-process
observations, not controlled hardware benchmarks. Hardware: 16.8 GB system RAM,
RTX 3050 Ti Laptop 4 GB; retrieval used CPU rather than this GPU.

## Source inspection of all 30 hybrid responses

The explicitly agent-labeled audit records 11 correct answers, seven partially
correct answers, two incorrect answers, nine refusals, and one rejected output.
Among 27 answered claims, 19 were fully supported, seven partially supported,
and one unsupported under the published rubric. These are agent judgments,
not human claim-support measurements or a general accuracy estimate.

Examples include cognitive gaze features mislabeled as stylistic features,
incorrect expansion of RG, incomplete answers that merely restate the question,
retrieval misses causing false refusals, and over-refusal despite usable context.
A valid citation may support only part of a claim. A source-supported alternative
may also differ from an annotated evidence paragraph without being fabricated.

All 30 editable [human review cards](claim_review.md) include the questions,
references, agent judgments, claims, and original cited/supplied passages.

## Provenance and reporting versions

The original prediction and report directories remain intact. Frozen-input
hardening subsequently added actual local model/tokenizer/vector byte hashes.
Separately versioned reports were then created without any new model requests:
`validation-retrieval-scores-v2/` and `validation-qa-baseline-30-scores-v2/` under
`reports/runs/`. Every method metric exactly matches the original report.
Their manifests point to the original run/prediction hashes and identify the
current scorer. `report` rejects drift; `rescore` explicitly creates a new version.

The Groq baseline snapshot is `reports/runs/frozen_groq_baseline.json`, SHA-256
`b07979afdbbcacb5b66951ec825dcf2a103684e06d6287f244cf4f943f36aa27`.
This records the baseline for comparisons; it does not select a final candidate
or consume the held-out test pilot. No active provider/method change has been made.

## Review boundary

[The audit rubric](../docs/evaluation.md) separates correctness, source support,
and refusal behavior. `validation_agent_audit.jsonl` contains explicitly labeled
agent source inspections. Human claim-support metrics remain unavailable until
a human reviewer labels the claims; structural citation validity is a separate
metric. A valid source span alone does not establish a correct answer.
