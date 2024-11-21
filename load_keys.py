import os
from constants import ENCRYPTION_KEY,OPENAI_API_KEY,CLAUDE_API_KEY,TAVILY_API_KEY

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

    # File to store the encrypted API keys
    encrypted_file_path = 'api_keys.json'

    # Initialize the manager
    config_manager = EncryptedConfigManager(encrypted_file_path, ENCRYPTION_KEY)

    config_manager.update_key('OPENAI_API_KEY', OPENAI_API_KEY)
    config_manager.update_key('CLAUDE_API_KEY', CLAUDE_API_KEY)
    config_manager.update_key('TAVILY_API_KEY', TAVILY_API_KEY)
