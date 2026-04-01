import os
import json
import base64

# LOCAL SECRET VAULT SERVICE
# This module provides a localized vault for secret management.
# Designed for secure credential handling in enterprise environments.

GSM_VAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "secrets", "gsm_vault.json")

class SecretManagerVault:
    def __init__(self):
        os.makedirs(os.path.dirname(GSM_VAULT_PATH), exist_ok=True)
        if not os.path.exists(GSM_VAULT_PATH):
            # Seed with example secrets for the demo
            initial_vault = {
                "prd-hc-db-password": "enterprise_secret_pass_2024",
                "fin-api-token": "hc_sk_9a2f_verified_token",
                "supply-chain-key": "sc_9932_auth_key"
            }
            with open(GSM_VAULT_PATH, "w") as f:
                json.dump(initial_vault, f, indent=4)

    def access_secret_version(self, secret_id: str) -> str:
        """
        Retrieves a secret version from the local vault.
        """
        try:
            with open(GSM_VAULT_PATH, "r") as f:
                vault = json.load(f)
            return vault.get(secret_id, None)
        except Exception as e:
            print(f"Vault Error: {e}")
            return None

    def store_secret(self, secret_id: str, value: str):
        """
        Stores a new secret version in the local vault.
        """
        try:
            with open(GSM_VAULT_PATH, "r") as f:
                vault = json.load(f)
            vault[secret_id] = value
            with open(GSM_VAULT_PATH, "w") as f:
                json.dump(vault, f, indent=4)
            return True
        except Exception as e:
            print(f"Vault Error: {e}")
            return False

gsm_client = SecretManagerVault()

def get_gsm_secret(secret_id: str) -> str:
    """Entry point for the application to fetch secrets from the vault."""
    return gsm_client.access_secret_version(secret_id)
