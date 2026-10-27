# Data card

## Provenance and terms

PaperTrail uses the official QASPER v0.3 structured English research-paper
release from Ai2. The [official dataset card](https://huggingface.co/datasets/allenai/qasper)
lists CC BY 4.0. Cite [A Dataset of Information-Seeking Questions and Answers
Anchored in Research Papers](https://arxiv.org/abs/2105.03011). Paper titles and
source identifiers remain attached to passages. The code's MIT license does not
relicense input data or source papers; see [NOTICE](../NOTICE).

## Inventory and selection

Verified release: 888 train, 281 validation, and 416 test papers; 5,049 questions
in total. Deterministic pilot selection uses SHA-256 of seed, split, and paper ID,
with seed 42. It retains every question from each selected paper: 5/19 training
papers/questions, 30/92 validation, and 50/187 test. These are pilot subsets.

The runtime store contains 85 papers, 4,043 paragraph records, and 4,440 chunks.
Abstracts are separate source paragraphs; original text, section names, paragraph
IDs, hashes, and Python Unicode character offsets are retained. Normalization
does not replace original source text with model summaries. Duplicate text can
have multiple legitimate positions. Long paragraphs use overlapping token windows.

## Separation from benchmark labels

`data/corpus` and SQLite runtime tables contain document records. Questions,
annotator answers, evidence annotations, and answerability flags live separately
under `data/evaluation` and are consumed only by offline evaluation. The API/UI
do not load them. Runtime export allowlists corpus/index/model assets and omits
benchmark labels, raw release archives, provider keys, and private run logs.

## Supported use and limitations

One explicitly selected English NLP paper per question; text paragraphs only.
PDF extraction, OCR, image/table reasoning, cross-paper answers, and Persian input
support are outside version one. Paragraph citations are not PDF page coordinates.
Some questions need figures/tables or lack fully mapped text evidence. Multiple
annotators can disagree; complete text-only evidence is not available for every
question. Original annotations may omit other valid support.

All 30 hybrid validation responses have a clearly labeled agent audit accepted by
the user. Human support auditing remains unavailable. The held-out pilot stopped
after 154/187 attempts at the user's request; it is not a complete benchmark result.
No peer usability result is claimed; the user deferred that review.

Only a few attributed training-paper paragraphs are included in the offline demo.
Large raw releases, runtime stores, model files, and private request logs remain
ignored by Git. [Evaluation details](../reports/evaluation.md).
