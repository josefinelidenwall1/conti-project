import os
import logging
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

def get_database_credentials(vault_url):
    """Get database credentials from Azure Key Vault"""

    try:
        
        logger.info("Attempting to get credentials from Azure Key Vault...")

        credential = DefaultAzureCredential()
        secret_client=SecretClient(vault_url=vault_url, credential=credential)

        # get secrets from key vault

        host=secret_client.get_secret("host").value
        database=secret_client.get_secret("database").value
        user=secret_client.get_secret("user").value
        password=secret_client.get_secret("password").value
        port=secret_client.get_secret("port").value

        logger.info(f"Successfully retrieved credentials from key vault")
        logger.info(f"Connecting to: host={host}, database={database}, user={user}, port={port}")
        logger.debug(f"Password length: {len(password)} characters")
        return host, database,user,password,port
    except Exception as e:
        logger.warning(f"Coult not get credentials from Key Vault; {e}")
        raise e
    


if __name__ == "__main__":
    # Setup basic logging to see the output in your terminal
    logging.basicConfig(level=logging.INFO)
    
    MY_VAULT = "https://conti-vault.vault.azure.net/"
    
    try:
        creds = get_database_credentials(MY_VAULT)
        print(f"TEST SUCCESS: Received credentials for {creds[0]}")
    except Exception:
        print("TEST FAILED: Check the error logs above.")



#Testing script from Azure to test connection with key vault
""" keyVaultName = "conti-vault"
KVUri = f"https://conti-vault.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

secretName = "SECRET-NAME"
secretValue = "SECRET-VALUE"

print(f"Creating a secret in conti-vault called '{secretName}' with the value '{secretValue}' ...")

client.set_secret(secretName, secretValue)

print(" done.")

print(f"Retrieving your secret from conti-vaultE.")

retrieved_secret = client.get_secret(secretName)

print(f"Your secret is '{retrieved_secret.value}'.")
print(f"Deleting your secret from conti-vault ...")

poller = client.begin_delete_secret(secretName)
deleted_secret = poller.result()

print(" done.") """