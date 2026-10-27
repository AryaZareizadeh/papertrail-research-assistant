"""PaperTrail's reading interface. All answers come from the configured HTTP API."""

import os

import streamlit as st

from evidence_assistant.ui_client import ApiClient, UIError, highlight_source


def clear_answer():
    for key in ("answer", "answer_error", "selected_citation"):
        st.session_state.pop(key, None)


def show_error(error):
    st.error(str(error))
    if error.request_id:
        st.caption(f"Request ID: {error.request_id}")


def main():
    st.set_page_config(page_title="PaperTrail", page_icon="📑", layout="wide")
    st.markdown(
        """<style>
        .stApp {background:#EDF2F6;color:#182934}
        .block-container {max-width:1400px;padding-top:2.4rem}
        h1,h2,h3 {color:#182934}
        .stText {white-space:pre-wrap;font-family:'Segoe UI',sans-serif;line-height:1.65}
        .papertrail-source {font-family:Georgia,serif;font-size:1.1rem;line-height:1.9;
          white-space:pre-wrap;background:#FFFFFF;padding:1.5rem;border-left:4px solid #176C73;
          overflow-wrap:anywhere}
        .papertrail-source mark {background:#F9E59C;color:#182934;padding:.12em 0}
        .stButton button:focus-visible {outline:3px solid #176C73;outline-offset:3px}
        </style>""",
        unsafe_allow_html=True,
    )
    st.title("PaperTrail")
    st.caption("Ask about a paper. Read the evidence behind each answer.")
    if os.environ.get("PAPERTRAIL_DEMO_MODE") == "recorded":
        st.warning(
            "Demo: a recorded answer and simulated refusal/error states. No model is called."
        )
        st.caption(
            "Try: What word embeddings were used? / What is the weather tomorrow? / "
            "Show a service failure. The saved answer used historical hybrid retrieval."
        )
    client = ApiClient(os.environ.get("PAPERTRAIL_API_URL", "http://127.0.0.1:8000"))
    try:
        papers = client.papers()
    except UIError as error:
        show_error(error)
        st.info("Start the API service, then refresh this page.")
        st.stop()
    if not papers:
        st.info("No papers are available yet. Prepare the document corpus and restart the API.")
        st.stop()
    by_id = {p.paper_id: p for p in papers}
    paper_id = st.selectbox(
        "Search and select a paper",
        list(by_id),
        format_func=lambda value: f"{by_id[value].title} ({value})",
        key="paper_id",
        on_change=clear_answer,
    )
    ready = True
    try:
        client.ready()
    except UIError as error:
        ready = False
        show_error(error)
    with st.form("question_form"):
        question = st.text_area(
            "Question",
            placeholder="Which datasets and evaluation metrics did the authors use?",
            max_chars=2000,
            key=f"question_{paper_id}",
            height=100,
        )
        submitted = st.form_submit_button(
            "Ask about this paper",
            type="primary",
            disabled=not ready,
        )
    if submitted:
        clear_answer()
        if not question.strip():
            st.warning("Enter a question about the selected paper.")
        else:
            with st.spinner("Reading the selected paper's evidence…"):
                try:
                    answer = client.ask(paper_id, question.strip())
                    st.session_state.answer = answer
                    if answer.citations:
                        st.session_state.selected_citation = answer.citations[0].chunk_id
                except UIError as error:
                    st.session_state.answer_error = error
    if "answer_error" in st.session_state:
        show_error(st.session_state.answer_error)
    answer = st.session_state.get("answer")
    left, right = st.columns([1, 1.35], gap="large")
    with left:
        st.subheader("Answer")
        if answer is None:
            st.info("Select a paper and ask a question to begin.")
        elif answer.status == "insufficient_evidence":
            st.info(
                "The retrieved passages do not provide sufficient evidence to answer this question."
            )
        else:
            sources = {c.chunk_id: (i, c) for i, c in enumerate(answer.citations, 1)}
            for claim_index, claim in enumerate(answer.claims):
                st.text(claim.text)
                for chunk_id in claim.citation_chunk_ids:
                    if chunk_id not in sources:
                        st.error("This answer contains a source link that cannot be displayed.")
                        continue
                    number, citation = sources[chunk_id]
                    if st.button(
                        f"Source {number}: {citation.section_name}",
                        key=f"{answer.request_id}_{claim_index}_{chunk_id}",
                    ):
                        st.session_state.selected_citation = chunk_id
        if answer is not None:
            if answer.model_id == "simulated refusal state":
                st.caption("Simulated response; timing is not a model measurement.")
            else:
                timing_label = (
                    "Recorded response time"
                    if os.environ.get("PAPERTRAIL_DEMO_MODE") == "recorded"
                    else "Response time"
                )
                st.caption(f"{timing_label}: {answer.latency_ms / 1000:.2f} seconds")
            with st.expander("Technical details"):
                st.json(
                    {
                        "model": answer.model_id,
                        "retrieval": answer.method,
                        "index": answer.index_version,
                        "prompt": answer.prompt_version,
                        "request_id": answer.request_id,
                    }
                )
    with right:
        st.subheader("Source passage")
        selected = st.session_state.get("selected_citation")
        citation = (
            next((c for c in answer.citations if c.chunk_id == selected), None) if answer else None
        )
        if citation is None:
            st.caption("Source links beside an answer open the original passage here.")
        else:
            try:
                source = client.paragraph(paper_id, citation.paragraph_id)
                highlighted = highlight_source(source, citation)
                st.text(by_id[paper_id].title)
                st.caption(f"{source.section_name}, paragraph {source.paragraph_index + 1}")
                st.markdown(
                    f'<div class="papertrail-source">{highlighted}</div>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    "The highlight identifies the cited span. Read the context to judge the claim."
                )
                with st.expander("Original plain text"):
                    st.text(source.text)
            except UIError as error:
                show_error(error)


if __name__ == "__main__":
    main()
