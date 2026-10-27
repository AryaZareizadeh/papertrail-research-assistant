# Exploratory usability feedback

Status: interface implemented; the user explicitly deferred peer review on
27 October 2026. Do not interpret
agent/software checks as peer feedback or demonstrated productivity improvement.

Ask two or three people who have not read the selected paper to try the interface.
Use [demo instructions](../docs/demo.md). Collect the notes below for each person;
do not include private names or information without their permission.

| Reviewer alias | Paper | Exact question | Confusing behavior | Did the evidence help verify the answer? | Suggested change |
| --- | --- | --- | --- | --- | --- |
| Pending | | | | | |
| Pending | | | | | |
| Optional third reviewer | | | | | |

Observe whether they can select a paper, distinguish a claim from its evidence,
open another citation, read surrounding text, and distinguish insufficient
evidence from a service failure. Record disagreements rather than assuming the
model's interpretation is correct. Feedback is exploratory, not a controlled
productivity study. Human claim-support scores remain unavailable separately.

Agent verification: synthetic AppTest checks cover question submission, citation
selection without regeneration, clearing results on a paper change, and distinct
refusal/error states. Real browser checks covered the recorded answer, a second
source selection with highlighted original text, and simulated refusal/error
states at a narrow viewport. A dark-theme contrast issue was corrected with an
explicit light theme. These checks are not independent peer feedback.

See the [captured walkthrough](demo/index.html) and [18-second frame sequence](demo/walkthrough.gif).
