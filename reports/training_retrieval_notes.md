# Initial training-only BM25 inspection

Date: 26 October 2026. These observations cover the top-ranked passage for the
first ten questions from the deterministic five-paper training selection.
This is exploratory inspection, not validation/test scoring or answer evaluation.
Full top-five records are local in `reports/runs/training_bm25_inspection.json`.

| Question topic | Top-passage observation |
| --- | --- |
| Vietnamese NER: word embeddings | Relevant: identifies the KP and EG embedding sources; does not include all construction details. |
| Vietnamese NER: error types | Partial: conclusion names the model and error analysis but omits the requested error categories. |
| Vietnamese NER: comparative improvement | Insufficient: identifies the compared systems but provides no numerical improvement. The training reference includes table evidence, outside strict text-only support. |
| RL: evidence for robustness | Partial: abstract repeats the robustness claim but does not show the experimental comparison supporting it. |
| RL: amount of performance improvement | Insufficient: abstract has no quantitative improvement; training annotation is unanswerable. |
| RL: convergence speed difference | Insufficient: abstract claims faster convergence without quantifying it. |
| RL: experiments performed | Partial: abstract supplies broad context but no experiment design. |
| RL: natural-language state representation | Partial: abstract names the representation but omits the construction mechanism. |
| Story generation: human interaction | Relevant: describes interfaces, model selection, planning, editing, and user control. Passage starts mid-paragraph window; source offsets retain surrounding context. |
| Story generation: story evaluation | Irrelevant to evaluation: passage describes generation and editing workflow. |

The repeated retrieval of the RL abstract illustrates lexical matching to question
wording without necessarily finding supporting detail. Dense/hybrid comparison,
claim-support auditing, and measured refusal behavior have not run.

## Verified corpus/chunk setup

- Observed QASPER papers/questions/annotations: train 888/2593/2675,
  validation 281/1005/1764, test 416/1451/3554.
- Pilot: 5 train, 30 validation, 50 test papers; all selected questions retained.
- Stored 4,043 paragraphs and 4,440 chunks; 59 blank paragraphs remain stored
  without searchable chunks; 427 paragraphs required multiple windows.
- All 4,440 source spans matched original SQLite paragraphs.
- Largest actual embedding-tokenizer input: 194 tokens including special tokens;
  prepared sentence-transformer input limit: 256.
- Tokenizer/model revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Model weights and actual dense/hybrid retrieval were verified during the
  subsequent Task 4 audit. No test answers were used for configuration choices
  or these training inspections.

QASPER provenance and attribution: [official dataset card](https://huggingface.co/datasets/allenai/qasper),
Dasigi et al., 2021. Dataset terms: CC BY 4.0; separate from this project's code.

## Subsequent real dense/hybrid smoke check

Pinned MiniLM built 4,440 normalized 384-dimensional vectors on CPU. The same ten
training questions were inspected with all three retrieval methods, each scoped
to its selected paper. Dense retrieval's top result found the explicit NER error
categories where BM25 returned a broad conclusion. Hybrid's top result for that
question instead discussed error-evaluation metrics, illustrating a fusion miss.
All methods still returned generation-workflow text for the story-evaluation
question. Qualitative examples do not establish that one method is better overall.

Warm retrieval timings for these ten questions (p50/p95, milliseconds): BM25
3.69/4.81; dense 51.69/129.50; hybrid 35.05/51.18. The first index build took
68.58 seconds including 11.68 seconds of model/library loading; build work excluding
load took 56.90 seconds. This small exploratory sample is not a latency benchmark.
Machine-readable details remain local in `reports/runs/task4_audit.json`.
