import time
import streamlit as st
from config_manager import EncryptedConfigManager
from constants import ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY, GEMINI_DEFAULT_SETTINGS, GEMINI_MODELS ,OPENAI_DEFAULT_SETTINGS, CLAUDE_DEFAULT_SETTINGS, OPENAI_MODELS, CLAUDE_MODELS
from query_engine import reset_collection

def render_sidebar():
    with st.sidebar:
        st.header("Input Section")
        
        # Button to open API key management dialog
        col1, col2, col3 = st.columns(3)
        with col1:
            openai_dialog = st.button("🔑 OpenAI Key", key="manage_openai_key_button")
        with col2:
            claude_dialog = st.button("🔐 Claude Key", key="manage_claude_key_button")
        with col3:
            gemini_dialog = st.button("🗝️ Gemini Key", key="manage_gemini_key_button")
        
        
        # Conditional dialogs for API key input
        if openai_dialog:
            key_management("OPENAI")
        if claude_dialog:
            key_management("CLAUDE")
        if gemini_dialog:
            key_management("GEMINI")
        
        col4, col5 , col6 = st.columns(3)
        with col4:
            openai_config = st.button("⚙️ OpenAI Settings", key="manage_openai_config_button")
        with col5:
            claude_config = st.button("🛠️ Claude Settings", key="manage_claude_config_button")
        with col6:
            gemini_config = st.button("🔧 Gemini Settings", key="manage_gemini_config_button")
        
        if openai_config:
            openai_config_management()
            
        if claude_config:
            claude_config_management()
        
        if gemini_config:
            gemini_config_management()


        uploaded_files = st.file_uploader("Upload File",
                                          accept_multiple_files=True,
                                          type=["pdf", "docx", "doc"],
                                          key="uploaded_files")
        
        if uploaded_files:

            # Removing ids in the prompt file mapping for subchapter configuration
            current_file_ids = {file.file_id for file in uploaded_files}
            if 'prompt_file_mapping' in st.session_state:
                for key in list(st.session_state.prompt_file_mapping.keys()):
                    # Filter out file IDs that are no longer in the uploaded files
                    st.session_state.prompt_file_mapping[key] = [
                        file_id for file_id in st.session_state.prompt_file_mapping[key] 
                        if file_id in current_file_ids
                    ]

            print("After:",st.session_state.prompt_file_mapping)
        
        text_area = st.text_area("Provide sub chapters separated by |")
        textsplit = text_area.split("|") if text_area else []

        prompt_config = st.button("💬 Sub chapters Configuration", key="manage_prompt_config_button")
        if prompt_config:
            prompt_config_management(textsplit)

        st.toggle(
            label="Search the Internet for information",
            key="search_engine"
        )

        st.selectbox(
            label="Choose LLM provider",
            options=("OPENAI", "CLAUDE","GEMINI"),
            key="llm_provider"
        )
        
        if st.button("Clear memory"):
            st.session_state.all_documents = {}
            st.session_state.generated_responses = {}
            st.session_state.documents_ready = False
            reset_collection()
        
        generate_button = st.button('Generate documents')

        download_button_placeholder = st.empty()
    
        if "token_warnings" in st.session_state and st.session_state.token_warnings:
            st.warning("⚠️ Some prompts with selected files exceed the token limit. Please adjust the configuration.")
            
            for prompt, file_ids in st.session_state.token_warnings.items():
                file_names = [file.name for file in uploaded_files if file.file_id in file_ids]
                st.write(f"Sub chapters: '{prompt}'\n exceeds token limit with files: {', '.join(file_names)}")

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



@st.dialog("OpenAI Configuration")
def openai_config_management():
    st.write("OpenAI Model Configuration")
    st.write("") 

    selected_model = st.selectbox(
        "Select OpenAI Model",
        options=OPENAI_MODELS,
        index=OPENAI_MODELS.index(st.session_state.openai_config["model"]),
    )
    # Add configuration for temperature, Max Tokens, Top P, Presence Penalty, Frequency Penalty
    
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=st.session_state.openai_config["temperature"], step=0.01)
    max_tokens = st.slider("Max Tokens", min_value=1, max_value=4096, value=st.session_state.openai_config["max_tokens"], step=1)
    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=st.session_state.openai_config["top_p"], step=0.01)
    presence_penalty = st.slider("Presence Penalty", min_value=-2.0, max_value=2.0, value=st.session_state.openai_config["presence_penalty"], step=0.01)
    frequency_penalty = st.slider("Frequency Penalty", min_value=-2.0, max_value=2.0, value=st.session_state.openai_config["frequency_penalty"], step=0.01)

    if temperature != OPENAI_DEFAULT_SETTINGS["temperature"] and top_p != OPENAI_DEFAULT_SETTINGS["top_p"]:
        st.warning("⚠️ It's generally recommended to alter either Temperature or Top P, but not both simultaneously. These parameters serve similar purposes in controlling randomness.")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Reset",use_container_width=True):
            st.session_state.openai_config.update(OPENAI_DEFAULT_SETTINGS)
            st.success("OpenAI settings reset to default values")
            time.sleep(2)
            st.rerun()

    with col2:
        if st.button("Save",use_container_width=True):
            st.session_state.openai_config["model"] = selected_model
            st.session_state.openai_config["temperature"] = temperature
            st.session_state.openai_config["max_tokens"] = max_tokens
            st.session_state.openai_config["top_p"] = top_p
            st.session_state.openai_config["presence_penalty"] = presence_penalty
            st.session_state.openai_config["frequency_penalty"] = frequency_penalty

            st.success("OpenAI configuration saved!")

@st.dialog("Claude Configuration")
def claude_config_management():
    st.write("Claude Model Configuration")


    selected_model = st.selectbox(
        "Select Claude Model",
        options=CLAUDE_MODELS,
        index=CLAUDE_MODELS.index(st.session_state.claude_config["model"])
    )

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=st.session_state.claude_config["temperature"], step=0.01)
    max_tokens = st.slider("Max Tokens", min_value=1, max_value=4096, value=st.session_state.claude_config["max_tokens"], step=1)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Reset",use_container_width=True):
            st.session_state.claude_config.update(CLAUDE_DEFAULT_SETTINGS)
            st.success("Claude settings reset to default values")
            time.sleep(2)
            st.rerun()
    with col2:
        if st.button("Save",use_container_width=True):
            st.session_state.claude_config["model"] = selected_model
            st.session_state.claude_config["temperature"] = temperature
            st.session_state.claude_config["max_tokens"] = max_tokens
            st.success("Claude configuration saved!")

@st.dialog("Gemini Configuration")
def gemini_config_management():
    st.write("Gemini Model Configuration")

    selected_model = st.selectbox(
        "Select Gemini Model",
        options=GEMINI_MODELS,
        index=GEMINI_MODELS.index(st.session_state.gemini_config["model"])
    )
    
    col1,col2 = st.columns([1,1])
    with col1:
        if st.button("Reset",use_container_width=True):
            st.session_state.gemini_config.update(GEMINI_DEFAULT_SETTINGS)
            st.success("Gemini settings reset to default values")
            time.sleep(2)
            st.rerun()
    with col2:
        if st.button("Save",use_container_width=True):
            st.session_state.gemini_config["model"] = selected_model
            st.success("Gemini configuration saved!")

@st.dialog("Prompt Configuration")
def prompt_config_management(textsplit):
    if len(textsplit) == 0:
        st.write("No sub chapters provided")
        return
    
    if len(st.session_state.get('uploaded_files', [])) == 0:
        st.write("No files uploaded")
        return
    
    st.write("Configure each prompt with file selection")

    # Create a dictionary of file_id to file_name for easier display
    uploaded_files = st.session_state.get('uploaded_files', [])
    file_options = {
        file.file_id: file.name 
        for file in uploaded_files
    }

    # Initialize prompt_file_mapping in session state if it doesn't exist
    if 'prompt_file_mapping' not in st.session_state:
        st.session_state.prompt_file_mapping = {}
    
    # Create a temporary dictionary to store selections
    temp_mapping = {}

    for i, split in enumerate(textsplit):
        prompt = split.strip()
        st.subheader(f"Configuration for: {prompt}")
        
        # Modified to select all files by default if no previous selection exists
        default_selection = st.session_state.prompt_file_mapping.get(i, [])
        selected_files = st.multiselect(
            f"Select files for {prompt}",
            options=list(file_options.keys()),
            format_func=lambda x: file_options[x],
            default=default_selection,
            key=f"files_{i}"
        )
        
        temp_mapping[i] = selected_files
    
    if st.button("Save Configuration"):
        # Only update session state when save is clicked
        st.session_state.prompt_file_mapping = temp_mapping.copy()
        st.success("Subchapters configuration saved!")
        # st.write("Current mapping:")
        # st.json(st.session_state.prompt_file_mapping)
