import os
import json
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import BlobContainer
from azure.storage.blob import BlobClient, BlobServiceClient
CONFIG_FILE = (r"C:\Users\JesseNurminen\OneDrive - Skillio Oy\Desktop\week3gp\conti-project\config.json")
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    subscription_id = config['azure']['subscription_id']
    RESOURCE_GROUP_NAME = config['azure']['resource_group_name']
    STORAGE_ACCOUNT_NAME = config['azure']['storage_account_name']
    STORAGE_ACCOUNT_URL = config['azure']['storage_account_url']
    QUEUE_URL = config['azure']['queue_url']
    CONTAINER_NAME = config['azure']['container_name']
    AZURE_STORAGE_BLOB_URL = config['azure']['azure_storage_blob_url']
    LOCATION = config['location']
    print('Loaded configs from file succesfully')
else:
    print(f"'{CONFIG_FILE}' not found")

credential = DefaultAzureCredential()
storage_client = StorageManagementClient(credential, subscription_id)
#-----------------------------------------------------------------------

def create_storage_account():
    print(f"Creating storage account: {STORAGE_ACCOUNT_NAME} in {RESOURCE_GROUP_NAME}...")

    storage_async_operation = storage_client.storage_accounts.begin_create(
        RESOURCE_GROUP_NAME,
        STORAGE_ACCOUNT_NAME,
        {
            "location": LOCATION,
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2",
            "properties": {
                "access_tier": "Hot"
            }
        }
    )

    storage_account = storage_async_operation.result()
    print(f"Successfully created storage account: {storage_account.name}")
    return storage_account

#-------------

def upload_file(local_file_path): #
    storage_account_name = "stcontigroupone001" #update name
    container_name = "conti-container" #check if exists, if not create one
    blob_name = os.path.basename(local_file_path)

    if not os.path.isfile(local_file_path):
        raise FileNotFoundError(f"File not found: {local_file_path}")

    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=credential
    )

    try:
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            print(f"Container '{container_name}' does not exist. Creating it...")
            container_client.create_container()

        with open(local_file_path, "rb") as data:
            container_client.upload_blob(
                name=blob_name,
                data=data,
                overwrite=True
            )

        print(f"Uploaded '{local_file_path}' as '{blob_name}'")

    except Exception as e:
        print(f"An error occurred: {e}")


upload_file(r"C:\Users\JesseNurminen\OneDrive - Skillio Oy\Desktop\week3gp\conti-project\schemasfordbtables.sql")