"""Preview and confirm imports through the API; no local corpus access."""

import streamlit as st

from evidence_assistant.paper_import import MAX_PDF_BYTES
from evidence_assistant.ui_client import UIError


def clear_preview():
    for key in ("import_preview", "import_title", "import_error"):
        st.session_state.pop(key, None)


def _show_error(error):
    st.error(str(error))
    if error.request_id:
        st.caption(f"Request ID: {error.request_id}")


def show_import(client):
    if notice := st.session_state.pop("import_notice", None):
        st.success(notice)
    with st.expander("Add a paper"):
        st.caption("Upload a PDF or import an arXiv paper, check the text, then save it.")
        pdf_tab, arxiv_tab = st.tabs(["Upload PDF", "arXiv link"])
        with pdf_tab:
            upload = st.file_uploader("PDF file", type=["pdf"], key="import_file",
                                      on_change=clear_preview, max_upload_size=20)
            st.caption("Selectable-text PDFs only · up to 20 MiB and 100 pages · no OCR")
            if st.button("Preview PDF", disabled=upload is None):
                clear_preview()
                try:
                    if upload.size > MAX_PDF_BYTES:
                        raise UIError("Choose a PDF smaller than 20 MiB.")
                    with st.spinner("Extracting text from the PDF…"):
                        st.session_state.import_preview = client.preview_pdf(
                            upload.getvalue(), upload.name
                        )
                except UIError as error:
                    st.session_state.import_error = error
        with arxiv_tab:
            link = st.text_input("arXiv link or ID", key="arxiv_input",
                                 placeholder="https://arxiv.org/abs/2401.12345",
                                 on_change=clear_preview)
            if st.button("Preview arXiv paper", disabled=not link.strip()):
                clear_preview()
                try:
                    with st.spinner("Downloading the arXiv PDF and extracting text…"):
                        st.session_state.import_preview = client.preview_arxiv(link.strip())
                except UIError as error:
                    st.session_state.import_error = error
        if "import_error" in st.session_state:
            _show_error(st.session_state.import_error)
        preview = st.session_state.get("import_preview")
        if preview is None:
            return
        st.subheader("Check before adding")
        st.caption(
            f"{preview.pages} pages · {preview.text_pages} pages with text · {preview.origin}"
        )
        for warning in preview.warnings:
            st.caption(warning)
        st.code(preview.preview_text, language=None, wrap_lines=True, height=260)
        if preview.preview_truncated:
            st.caption(
                "Preview shows the first 20,000 characters; the full extracted text is saved."
            )
        st.text_input("Paper title", value=preview.title, max_chars=300, key="import_title")
        if st.button("Add to collection", type="primary"):
            try:
                with st.spinner("Indexing this paper for questions…"):
                    saved = client.confirm_import(preview.preview_id, st.session_state.import_title)
                st.session_state.paper_id = saved.paper.paper_id
                for key in ("answer", "answer_error", "selected_citation"):
                    st.session_state.pop(key, None)
                clear_preview()
                st.session_state.import_notice = (
                    "This PDF is already in your collection. Selected the existing paper."
                    if saved.already_exists else f"Added: {saved.paper.title}"
                )
                st.rerun()
            except UIError as error:
                _show_error(error)
