import streamlit as st
from query_engine import reset_collection

def render_sidebar():
    with st.sidebar:
        st.header("Input Section")
        
        # Button to open API key management dialog
        open_dialog_button = st.button("Manage API Key", key="manage_api_key_button")
        
        # Conditional dialog for API key input
        if open_dialog_button:
            key_management()
        
        uploaded_files = st.file_uploader("Upload File",
                                          accept_multiple_files=True,
                                          type=["pdf", "docx", "doc"],
                                          key="general_agent")
        
        text_area = st.text_area("Provide sub chapters separated by |")
        textsplit = text_area.split("|") if text_area else []

        st.toggle(
            label="Search the Internet for information",
            key="search_engine"
        )

        st.selectbox(
            label="Choose LLM provider",
            options=("OPENAI", "CLAUDE"),
            key="llm_provider"
        )
        
        if st.button("Clear memory"):
            st.session_state.all_documents = {}
            st.session_state.generated_responses = {}
            st.session_state.documents_ready = False
            reset_collection()
        
        generate_button = st.button('Generate documents')

        download_button_placeholder = st.empty()

    return uploaded_files, textsplit, generate_button, download_button_placeholder

@st.dialog("API Key Management")
def key_management():
    api_key = st.text_input("Enter your API Key", type="password", key="api_key") 
    # Provide feedback on API key presence
    if api_key:
        st.success("API Key set!")
    else:
        st.warning("Please enter an API Key.")

    if st.button("Submit"):
    #    Processing the submission flow
        st.rerun()      