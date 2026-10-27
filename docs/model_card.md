# Model and pipeline card

## Intended use

Help a researcher inspect short answers about one selected English NLP paper.
Each answer claim has source links; the reader remains responsible for checking
whether the original passage supports the interpretation. Citation validation
establishes source identity and span integrity, not semantic correctness.

## Selected components

| Component | Identity and role |
| --- | --- |
| Encoder | `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; normalized 384-dimensional CPU embeddings. |
| Retriever | Dense cosine retrieval, restricted to the selected paper, top five; whole-chunk token budgeting. BM25/hybrid remain reproducible baselines. |
| Generator | Groq `openai/gpt-oss-20b`, explicitly selected by the user. Hosted weights are not locally pinned or shipped. |
| Generation tokenizer | `openai/gpt-oss-20b`, revision `6cee5e81ee83917806bbde320786a8fb61efebee`; pinned native chat template, locally prepared. |
| Prompt/output | evidence-v1, strict structured claims and chunk IDs, temperature 0, low reasoning effort, 512 output tokens. |
| Budgets | 4,096 total context, 1,536 evidence tokens, 256 safety reserve; calibrated input accounting. |
| Storage | SQLite documents/chunks; request logs in a separate writable location. PostgreSQL is a future migration. |

MiniLM's [official card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
lists Apache 2.0. GPT-OSS tokenizer/model terms are available in its
[official card](https://huggingface.co/openai/gpt-oss-20b); provider-service terms
are separate. Only MiniLM weights and the generation tokenizer are prepared
locally. Container export preserves their bytes and calibration while rewriting
machine-specific snapshot paths. No fine-tuning is performed.

## Operation and measured behavior

The generator receives the question and retrieved passages from the selected
paper. It never receives benchmark answers or gold evidence. Source contents are
treated as data rather than instructions. A malformed claim/citation is rejected;
an unavailable provider is a service error, not a deliberate refusal. Hosted
model revisions/fingerprints and token counts are recorded where returned.

Selected dense baseline: Answer F1 0.3917 on 30 validation questions; zero model
errors; warm p95 2.93 seconds. This is lexical F1, not accuracy or a full-benchmark
claim. See [the report](../reports/evaluation.md) for denominators, tradeoffs,
agent-audit labels, and the incomplete held-out pilot. Human support and peer
usability measurements remain unavailable. New hosted model tests were stopped
at the user's request; deterministic software checks use fake responses.

## Known limits

Retrieval can omit necessary text, a chunk may cover only part of a paragraph,
and an answer can misinterpret a valid source. The validation audit observed
partial support, unsupported claims, wrong interpretations, and false refusals.
Free hosted routes can throttle; the interrupted held-out run retained two 429
errors. Public benchmark contamination and hosted backend variation are unknown.
This system is not configured for public multi-user hosting or professional
decision-making. Its interface exposes the source so failures remain inspectable.
