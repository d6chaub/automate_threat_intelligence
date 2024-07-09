import logging
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class SecretsManager:
    """
    Singleton class to manage the lifetime of the Azure KeyVault client across the application.
    
    Secrets are accessed dynamically from the KeyVault using the Azure SDK, and are not cached in memory.

    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecretsManager, cls).__new__(cls)
            cls._instance.keyvault_client = None
            cls._instance._initialize_keyvault_client()
        return cls._instance
    
    def _initialize_keyvault_client(self):
        key_vault_name = os.getenv("KeyVault")
        if key_vault_name is None:
            raise ValueError("KeyVault environment variable not set")
        key_vault_url = f"https://{key_vault_name}.vault.azure.net/"

        credential = DefaultAzureCredential() # Use Azure managed identity to allow intra-resource access, without keys.
        keyvault_client = SecretClient(vault_url=key_vault_url, credential=credential)
        self.keyvault_client = keyvault_client

    def get_secret_value(self, secret_name: str):
        return self.keyvault_client.get_secret(secret_name).value
        
                
