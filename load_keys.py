import os
from constants import ENCRYPTION_KEY, GEMINI_API_KEY,OPENAI_API_KEY,CLAUDE_API_KEY,TAVILY_API_KEY,ENCRYPTED_KEYS_FILE_PATH

from config_manager import EncryptedConfigManager

def load_keys():

    if not ENCRYPTION_KEY:
        raise ValueError("Encryption key not found in environment variables")
    
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    
    if not CLAUDE_API_KEY:
        raise ValueError("Claude API key not found in environment variables")
    
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")


    # Initialize the manager
    config_manager = EncryptedConfigManager(ENCRYPTED_KEYS_FILE_PATH, ENCRYPTION_KEY)

    config_manager.update_key('OPENAI_API_KEY', OPENAI_API_KEY)
    config_manager.update_key('CLAUDE_API_KEY', CLAUDE_API_KEY)
    config_manager.update_key('TAVILY_API_KEY', TAVILY_API_KEY)
    config_manager.update_key('GEMINI_API_KEY', GEMINI_API_KEY)
