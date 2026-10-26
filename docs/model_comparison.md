# Optional Requesty/Nemotron comparison

Groq remains the application default. These commands opt into a separate experiment
and do not edit `config.yaml` or replace its GPT-OSS tokenizer/calibration.

Save `REQUESTY_API_KEY` in the ignored `.env` file, then run:

```powershell
.\.venv\Scripts\python.exe -m evidence_assistant.cli prepare-candidate-tokenizer
.\.venv\Scripts\python.exe -m evidence_assistant.cli calibrate-candidate --interval-seconds 15
.\.venv\Scripts\python.exe -m evidence_assistant.cli compare-models --source-run-dir reports/runs/validation-qa-baseline-30 --method hybrid --output reports/runs/nemotron-fixed-context-30 --interval-seconds 15
```

Calibration reuses successful compatible training probes after interruption, then
makes an independent validation probe. Use `calibrate-candidate --fresh` to re-probe
all four after provider token-format changes. No benchmark answers enter calibration.
Only tokenizer/config/template files are downloaded; generation weights stay hosted.

The exact route is `nvidia/nemotron-3-ultra-550b-a55b`. Before dispatch, the adapter
checks its authenticated catalog entry has zero input/output price at every listed
tier. It does not use a bare model name, routing policy, paid fallback, or tools.
Actual cost, usage, errors, and provider identity are retained when returned.
Known nonzero cost stops dispatch even if the response is invalid or truncated.

The [free-model documentation](https://docs.requesty.ai/features/free-models) lists
organization quotas; account/provider capacity can differ. Quota errors stop the
batch and remain failed cases. Repeating the comparison command resumes missing
cases in the original output directory. An atomic checkpoint transaction protects
completed checkpoints if prediction/manifest publication is interrupted. Changed
source data, settings, tokenizer calibration, code, or passages reject resume.

## Format and reasoning differences

The live catalog marks this route's JSON object and JSON schema support false.
The candidate therefore receives the same claim/citation schema as an explicit
system formatting instruction, followed by local Pydantic and source validation.
Groq uses native strict JSON schema. Questions and supplied passages are identical;
this is a backend comparison with a declared format adaptation.

The NVIDIA-native `enable_thinking=False` flag alone still returned reasoning in
our Requesty probe and exhausted the 512-token budget on a training question.
Requesty's documented [`reasoning_effort: none`](https://docs.requesty.ai/features/reasoning)
suppressed it in a diagnostic. The candidate sends both settings; Groq retains its
low-effort request. These provider-specific options are recorded explicitly.

## Verified preflight

The pinned NVIDIA tokenizer revision is `77df655d5e9f8362164ed14dd8b48f8bce657498`.
Three training probes matched provider input counts with offset zero. A fourth
independent prompt matched at 1,314 tokens, and loading the saved calibration
reproduced the count. All four reported zero cost. One earlier rate-limit failure
and the initial truncated response remain in the run history.

The comparison reads each baseline's saved supplied chunks in their original
order and verifies them against SQLite. It never retrieves again or silently drops
context. A candidate budget failure remains an error, rather than receiving easier
passages. Per-question results and paired metrics retain every selected case.

See [the preregistered hypothesis and decision rule](../reports/failure_analysis.md).
Human review is still unavailable; the user accepted explicitly labeled agent
inspection for this project milestone. No switch is justified by model size alone.
