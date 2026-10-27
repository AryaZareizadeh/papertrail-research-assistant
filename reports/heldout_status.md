# Held-out pilot — stopped at the user's request

The user requested no more tests on 27 October 2026. The queued evaluation process
was stopped before further requests: 154 attempts are saved and 33 questions
remain unattempted. Both rate-limit failures are retained. The held-out pilot is
incomplete; do not resume it or launch more model tests unless the user asks.
The operational notes below describe the earlier run and backoff plan.

Status recorded 27 October 2026, about 01:00 UTC. This is an operational progress
record, not a completed evaluation report or an interim quality comparison.

- Frozen candidate: Groq `openai/gpt-oss-20b` plus dense retrieval, code `7788140`.
- Freeze SHA-256: `878815f1e6e4d922661b3e2932f795db4d4a7f23512d5dc27bc462b01c47eeba`.
- Selection: all 187 questions from the deterministic 50-paper held-out pilot.
- Saved attempts: **154/187**; 152 completed model responses and two HTTP 429
  failures. **33 questions have not yet been attempted.**
- Known actual usage: 149,067 input plus 15,712 output tokens, totaling 164,779.
  Actual usage for the two rate-limit failures is unavailable.
- First throttle: 00:52:53 UTC, `Retry-After: 12`. After waiting, the same run
  resumed and completed two more questions. Second throttle: 00:55:35 UTC,
  `Retry-After: 402`. Both failures remain in the saved evaluation.

The unchanged CLI had been queued to resume only the 33 unsaved question IDs after a conservative
15-minute initial cooldown (approximately 01:10:35 UTC). Subsequent requests are
paced at 600 seconds. This operational backoff changes neither passages nor
generation/scoring settings. It may take roughly another five to six hours; more
provider throttling can stop dispatch again. The exact quota type was not returned
in the preserved diagnostics, so this is conservative pacing, not a claim about
when an account's quota resets. A read-only model-catalog probe succeeded but did
not include quota headers.

The [provider's rate-limit documentation](https://console.groq.com/docs/rate-limits)
describes organization-wide limits and Retry-After in seconds. No paid route,
fallback model, alternate key, or regenerated failed case is used.

Run directory: `reports/runs/final-test`. Log: `.cache/final-test.log`. The ignored
`.cache/resume_final_test.py` waits out the cooldown, then invokes the existing CLI
with `--interval-seconds 600`. The authoritative checkpoint and consumed-selection
marker must remain intact. Do not change main-checkout source/configuration/model/
index/data bytes until the run finishes, or its resume identity will no longer match.

The full held-out acceptance check was not completed; remaining inference was
waived by the user's instruction to stop. No partial quality score is being used
to choose settings.
The user subsequently confirmed Groq GPT-OSS-20B as the final model choice.
Implementation can continue with the incomplete pilot explicitly documented;
the stopped run is not a requirement to dispatch more inference before integration.
The reviewed Task 8 API draft is saved separately at `d004ee3` on `codex/api-draft`:
137 deterministic tests pass in both environments, real read-only HTTP checks pass,
and the live API question smoke remains unrun under the user's instruction.
