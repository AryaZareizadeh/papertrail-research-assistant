# Evidence viewer design

The approved Task 9 brief is the specification: one selected paper, one question,
readable claims, and original source paragraphs with exact cited spans. No model,
retrieval, or prompt controls belong in the question flow.

Design choice: a quiet reading desk with answers on the left and source evidence
on the right. On narrow screens the source follows the answer. A searchable paper
selector precedes the question. Source buttons stay beside the claim they support.
Evidence text remains complete, including surrounding context.

Palette: white `#FFFFFF`, cool paper `#EDF2F6`, ink `#182934`, teal `#176C73`,
source highlight `#F9E59C`, rule `#C8D4DF`. Segoe UI/system sans-serif for controls
and answers; Georgia/serif for the original passage. No remote font downloads.
Left-aligned text, comfortable line lengths, visible keyboard focus, restrained
rules, and no decorative animation or correctness badges.

```text
PaperTrail                         Evidence you can inspect
Search and select a paper [                                  ]
Question [                                                  ]
[Ask about this paper]

Answer                         | Source passage
Claim text [Source 1]           | Paper title / section / paragraph
Claim text [Source 2]           | Original text with <highlight> and context
Response time                  | Original plain text available
[Technical details]            |
```

Review against the brief: a generic dashboard would obscure the actual reading
task. This layout gives the original paragraph more space than the answer and
keeps citation selection in the claim's immediate context. Empty, insufficient-
evidence, service-error, and source-mismatch states each explain the next action.
Paper changes clear prior answers. Selecting evidence never regenerates an answer.
Only escaped source text enters the highlight HTML; offsets use Python Unicode
code points. Model text renders as plain text rather than executable markup.

The UI calls the API through `PAPERTRAIL_API_URL` (default localhost:8000). Hosted
generation remains in the API, with credentials absent from the UI process.
