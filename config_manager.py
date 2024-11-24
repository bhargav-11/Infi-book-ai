import json
import os
from cryptography.fernet import Fernet

class EncryptedConfigManager:
    def __init__(self, encrypted_file_path, encryption_key):
        self.encrypted_file_path = encrypted_file_path
        self.fernet = Fernet(encryption_key)

        # Load initial keys
        self.keys = self._load_keys()

    def _load_keys(self):
        """Load keys from the encrypted JSON file."""
        if not os.path.exists(self.encrypted_file_path):
            return {}  # Return an empty dictionary if the file doesn't exist
        with open(self.encrypted_file_path, 'r') as file:
            return json.load(file)

    def _save_keys(self):
        """Save the keys to the encrypted JSON file."""
        with open(self.encrypted_file_path, 'w') as file:
            json.dump(self.keys, file, indent=4)

    def get_key(self, key_name):
        """Decrypt and return the value of the specified key."""
        self.keys = self._load_keys()
        encrypted_value = self.keys.get(key_name)
        if encrypted_value:
            return self.fernet.decrypt(encrypted_value.encode()).decode()
        return None

    def update_key(self, key_name, key_value):
        """Encrypt and update the value of the specified key."""
        encrypted_value = self.fernet.encrypt(key_value.encode()).decode()
        self.keys[key_name] = encrypted_value

        # Save the updated keys to the file
        current_data = self._load_keys()
        current_data[key_name] = encrypted_value
        
        with open(self.encrypted_file_path, 'w') as file:
            json.dump(current_data, file, indent=4)

    def list_keys(self):
        """List all stored key names."""
        return list(self.keys.keys())

    def delete_key(self, key_name):
        """Delete a specific key from the file."""
        if key_name in self.keys:
            del self.keys[key_name]
            self._save_keys()