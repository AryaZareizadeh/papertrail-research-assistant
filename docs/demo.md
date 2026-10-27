# Try PaperTrail

Prepare the corpus/index/tokenizer artifacts using the README. Put `GROQ_API_KEY`
in the ignored `.env` file, then start these in separate terminals from the repo:

```powershell
python -m uvicorn evidence_assistant.api:app --host 127.0.0.1 --port 8000
python -m streamlit run src/evidence_assistant/ui.py --server.address 127.0.0.1 --server.port 8501
```

Open http://127.0.0.1:8501. Search for a paper by title or ID, ask one question,
and click a source button beside a claim. The original paragraph appears on the
right with the cited span highlighted. Expand “Original plain text” for an
unformatted copy. Changing papers clears the previous answer. Clicking sources
does not request a new answer. Technical details show the model, retrieval method,
index, prompt, and request ID; these controls do not change the evaluated settings.

`PAPERTRAIL_API_URL` sets the API address for the UI. `PAPERTRAIL_CONFIG` sets the
API configuration file. The UI does not load model weights or read the provider
key. A live question sends the selected question and retrieved paper passages to
Groq; source browsing alone does not make model calls.

An insufficient-evidence response is a deliberate answer state. A service failure
is an error banner, with a request ID when available. A source mismatch is also
an error; a highlight is never presented as proof of correctness.

No further hosted model tests are being run during development at the user's
request. Deterministic UI/API checks use synthetic responses.

## Offline walkthrough without a provider call

```powershell
python -m uvicorn tools.demo_api:app --host 127.0.0.1 --port 8001
```

In a separate terminal:

```powershell
$env:PAPERTRAIL_API_URL = 'http://127.0.0.1:8001'
$env:PAPERTRAIL_DEMO_MODE = 'recorded'
python -m streamlit run src/evidence_assistant/ui.py --server.address 127.0.0.1 --server.port 8501
```

Select the available paper and use these exact questions:

1. **What word embeddings were used?** Replays a saved Groq answer from a training
   paper. Click each source and read the original paragraph. This historical answer
   used hybrid retrieval; it is not a fresh run of the selected dense configuration.
2. **What is the weather tomorrow?** Shows a simulated insufficient-evidence
   response. It is a UI demonstration, not a newly measured model refusal.
3. **Show a service failure.** Shows a simulated rate-limit error and request ID.

The replay API serves only these examples; it cannot answer arbitrary questions.
It loads no model, reads no provider key, and sends no provider requests. The public
example paper text is QASPER v0.3, CC BY 4.0. Clear the two demo environment
variables before switching back to the normal API.

The [saved walkthrough](../reports/demo/index.html) and
[captured-frame GIF](../reports/demo/walkthrough.gif) show the answer, a selected
source, a simulated refusal, and a simulated failure. These are actual browser
captures assembled into an 18-second sequence, not a continuous screen recording.
Peer feedback was explicitly deferred by the user; the template remains in
[usability notes](../reports/usability.md).
