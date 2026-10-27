# Evaluation and controlled model comparison

The runtime service receives document text and the question. Only this offline
evaluator reads benchmark references. QASPER v0.3 pilot selections are saved under
`data/manifests/`; train is for debugging, validation for decisions, and test is
held out until the candidate is frozen.

## Reproduce or resume a validation run

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli evaluate-retrieval --split validation --methods bm25 dense hybrid --output reports/runs/validation-retrieval
.\.venv\Scripts\python.exe -m evidence_assistant.cli evaluate-qa --split validation --method hybrid --limit 3 --output reports/runs/validation-timing
.\.venv\Scripts\python.exe -m evidence_assistant.cli evaluate-qa --split validation --method hybrid --limit 30 --output reports/runs/validation-qa
.\.venv\Scripts\python.exe -m evidence_assistant.cli report --run-dir reports/runs/validation-qa
```

`--config` and `--manifest` are accepted by both evaluation commands. The default
manifest is the saved pilot selection for the requested split. `--limit` selects
the first N questions by SHA-256 of `seed:question_id`, before looking at labels;
the saved run manifest lists every selected question. Omit it to evaluate all
questions in the pilot. Use the same limit, seed, and manifest across methods.

The same answer service performs generation and citation checks. Retrieval-only
evaluation uses its shared whole-chunk context budget, so it scores supplied
passages after trimming. Generation uses the same model, prompt, and token limits
for every retrieval method. Each prediction saves the exact supplied passages,
IDs, source offsets, source/configuration hashes, and actual/estimated token usage.
These saved passages also permit a later model comparison with retrieval held fixed.

Every result is checkpointed. Repeating a command with its original output path
resumes missing cases and rejects changed settings, data, code, or selection.
Recorded errors remain failed cases. A quota error stops further requests; it
does not create fabricated refusals for the remaining questions. The report shows
missing cases separately. Pace requests with `--interval-seconds` to respect the
account's free limits. No paid fallback is configured.

## Scoring policy

`qasper-text-v1` maps full evidence strings exactly first, then permits only
whitespace split/join normalization. It retains all positional matches of repeated
paragraphs as alternatives. It does not fuzzy-match. Highlighted spans remain
separate; float markers and unmapped evidence are logged explicitly.

Paragraph retrieval scores use one intact annotator evidence set at a time and
take the best reference score. Duplicate chunks and repeated equivalent gold
paragraphs do not earn repeated credit. References with empty, float, or unmapped
evidence cannot provide a complete positive text target; excluded counts are
reported. Whole-selected-set scores retain all predictions. The strict text-only
slice excludes a question if any annotation has float evidence, unmapped evidence,
or an answerable reference without positive text evidence. These flags never turn
an answerable question into an unanswerable one.

Abstention precision, unanswerable recall, and false refusal use consensus labels.
Mixed annotations are counted separately. Service errors and missing predictions
remain distinct from deliberate insufficient-evidence answers. Structural citation
validity checks supplied chunk identity, original paragraph, offsets, and quote;
it does not establish semantic support.

Answer F1 and evidence F1 use the unmodified, Apache-licensed
[official evaluator](https://github.com/allenai/qasper-led-baseline/blob/e996b6c7b1b5f95d9308a74e3586416c6e780df1/scripts/evaluator.py),
pinned in `_vendor` with its license and SHA-256. Each method exports the expected
JSONL adapter format. Refusals become `Unanswerable`; service errors are omitted
from this adapter and receive the official missing-prediction zero. Missing/error
counts remain explicit in product metrics. Official evidence F1 has different
empty-reference behavior from the project's positive-evidence retrieval metrics;
keep the two separate.

Reporting validates scoring code/policy and saved scoring-input hashes. It rejects
changed inputs instead of overwriting a report under the original identity.
To apply a new scoring/reporting version, explicitly create a separate report:

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli rescore --source-run-dir reports/runs/validation-qa --output reports/runs/validation-qa-scores-v2
```

This copies unchanged scoring inputs and predictions, records their original
manifest/hash provenance, and publishes a new scoring identity without provider
calls. It refuses altered source inputs and never overwrites the original report.

## Claim-support audit

Review at least 30 validation responses, including errors/refusals and difficult
evidence cases. For each answered claim, read its cited source passages:

- **Fully supported:** the cited text supports every substantive part of the claim.
- **Partially supported:** it supports part, but a qualifier, entity, number, or
  inference exceeds the cited text.
- **Unsupported:** the citation is irrelevant, contradicts the claim, or does not
  establish the main assertion.

Judge question correctness separately from source support. A source-supported
statement may answer the wrong question. A different citation from the annotated
evidence may still be valid. Refusals have no claims to score; check whether their
supplied context justified refusing, and retain consensus false refusals in metrics.
Record reviewer identity and notes. Agent inspection and human review must be
labeled separately; an uncompleted human audit is reported as unavailable.

## Final test gate

After validation decisions in Task 7:

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli freeze --output reports/runs/frozen_candidate.json
.\.venv\Scripts\python.exe -m evidence_assistant.cli evaluate-qa --split test --manifest data/manifests/test_pilot.json --method dense --frozen-run-manifest reports/runs/frozen_candidate.json --output reports/runs/final-test --interval-seconds 20
```

The frozen manifest binds configuration, dataset selections, corpus/index/model
metadata, tokenizer calibration, prompt, dependency lock, code, and scoring rules.
Actual local embedding weight, tokenizer, and vector file hashes are included,
so unchanged revision labels cannot conceal changed bytes. Hosted weights cannot
be pinned locally; the requested model ID and returned fingerprint are recorded.
The test gate rejects changed inputs, arbitrary test selections, limits, or a
different retrieval method. A consumed-selection marker allows resuming the
original output directory and blocks another run of the same held-out pilot.
Later test-informed development requires a genuinely new held-out selection.

## Later Requesty/Nemotron comparison

Keep Groq active until the baseline is evaluated. Before using Requesty, verify
its exact free NVIDIA route, credentials, structured response support, and matching
token counter. Give both models the same selected questions and the baseline's
saved supplied passages, without re-retrieving. Hold prompt instructions and
effective evidence/output budgets fixed, while recording provider-specific format
options. Compare question correctness, claim support, false refusals, errors,
latency, and known token use. Switch only if the evidence supports the change.
