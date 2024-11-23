import streamlit as st
from config_manager import EncryptedConfigManager
from constants import ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY
from query_engine import reset_collection

def render_sidebar():
    with st.sidebar:
        st.header("Input Section")
        
        # Button to open API key management dialog
        col1, col2 = st.columns(2)
        with col1:
            openai_dialog = st.button("Configure OpenAI Key", key="manage_openai_key_button")
        with col2:
            claude_dialog = st.button("Configure Claude Key", key="manage_claude_key_button")
        
        # Conditional dialogs for API key input
        if openai_dialog:
            key_management("OPENAI")
        if claude_dialog:
            key_management("CLAUDE")
        
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
def key_management(provider):
    config_manager = EncryptedConfigManager(ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY)
    existing_key = config_manager.get_key(f"{provider}_API_KEY")

    
    api_key = st.text_input(
        f"Enter your {provider} API Key", 
        type="password",
        value=existing_key if existing_key else "",
        key=f"{provider}_API_KEY"
    )

    if st.button("Save"):
        if api_key:
            config_manager.update_key(f"{provider}_API_KEY", api_key)
            st.success(f"{provider} API Key saved successfully!")