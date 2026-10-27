# Fixed-context Groq/Nemotron comparison

Decision: 27 October 2026 (Tehran). Keep Groq as the active generation backend.
Nemotron showed useful quality gains, but the free route failed the preregistered
operational gate. This is a 30-question validation pilot with an explicitly
agent-labeled audit, not a general model ranking or a human evaluation.

Both backends received the same 30 questions and exact original hybrid passages,
in the same order. All 30 attempted cases passed byte/content identity checks.
Groq used native strict schema; Nemotron received the identical schema information
as a formatting instruction and used the same local source/citation validation.
The declared provider formatting/reasoning differences remain part of this backend
comparison. No model/provider switch was made during the experiment.

| Measure | Groq GPT-OSS-20B | Requesty Nemotron Ultra |
| --- | ---: | ---: |
| Whole-selected-set Answer F1 | 0.3417 | 0.3818 |
| Evidence F1 | 0.5484 | 0.5189 |
| Validated answered responses | 20/30 | 16/30 |
| Consensus false refusals | 5/23 | 4/23 |
| Consensus unanswerable recall | 0/2 | 2/2 |
| System/model errors | 1/30 | 5/30 |
| Warm p50 / p95, all cases | 1.41 / 2.40 s | 2.42 / 5.93 s |
| Displayed citation validity | 28/28 | 28/28 |

Nemotron's five errors were HTTP 429 responses, including attempts after cooldowns
and wider pacing. The provider returned only Too Many Requests, with no Retry-After
or more specific cause. They were retained and never regenerated into favorable
answers. Known-cost completions all reported zero cost (25 cases); actual usage
and cost are unavailable for five throttled cases. Known usage totaled 29,018
input and 2,628 output tokens, with exact counter matches on all 25 completions.
Served-case-only p95 was 6.37 seconds. Client pacing/cooldowns are outside per-case
latency; these figures do not establish sustained production throughput.

The lower false-refusal count is not wholly a quality gain: one Groq refusal became
a throttled request. Errors remain in the same 30-case denominator. Correct refusal
of the stylistic-feature and best-system questions is a genuine observed gain;
both previously received incorrect Groq answers. Neither backend correctly expanded
RG from the abbreviation-only context. Retrieval omissions could not be repaired by
changing the generator while holding passages fixed.

## Accepted agent audit

All 30 candidate responses were inspected using the same rubric as the Groq audit.
Candidate: 12 correct substantive answers, four partially correct, nine refusals,
and five service errors. Groq: 11 correct substantive answers, seven partially
correct, two incorrect, nine refusals, and one rejected output. Correct consensus
refusals add two correct responses for Nemotron and zero for Groq.

Candidate claims: 24 fully supported, four partially supported, zero unsupported,
out of 28. Groq claims: 19 fully supported, seven partially supported, one unsupported,
out of 27. Claim segmentation differs by model, so these counts are descriptive.
Judgments, including debatable reference mismatches, remain inspectable in
`nemotron_agent_audit.jsonl` and `validation_agent_audit.jsonl`. Human support
measurements remain unavailable.

The predeclared rule required at least two additional fully correct substantive
answers and no more than one error, alongside support/refusal and latency gates.
The candidate improved substantive answers by one and had five errors. It does not
qualify for the default backend despite better F1, safer refusals, and acceptable
served-case latency. It remains available as an opt-in experiment.

## Final retrieval selection

The prespecified Task 6 comparison used the same Groq model, prompt, 30 questions,
top-k, and budgets across BM25/dense/hybrid. Dense produced Answer F1 0.3917 versus
hybrid 0.3417, Evidence F1 0.6095 versus 0.5484, and zero versus one model error.
On all 92 validation questions, strict complete-evidence coverage was 32/66 versus
31/66, and recall 0.5162 versus 0.5056. Dense had one fewer evidence hit (36 versus
37), one additional false refusal (6/23 versus 5/23), and p95 2.93 versus 2.40 seconds.

Inspection confirmed a substantive gain on negated LAMA: dense supplied the actual
construction/comparison paragraph; hybrid supplied only broad summary/discussion.
Some F1 gains, such as dataset-size phrasing and shorter baseline lists, reflect
wording rather than improved factual correctness. This is a provisional pilot
choice, not statistical superiority.

Select **Groq + dense** for the final candidate. The only retained setting change
is retrieval_method; chunking, generator, prompt, budgets, and scoring stay fixed.
The rejected Nemotron experiment is separate from this selection among the already
measured baselines. Freeze before the once-only held-out pilot; do not tune against
its answers afterward.

Raw comparison: `reports/runs/nemotron-fixed-context-30/`, including atomic
checkpoints, immutable source bindings, paired metrics, and all five failures.
