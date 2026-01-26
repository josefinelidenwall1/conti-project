import os
import json
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import BlobContainer
from azure.storage.blob import BlobClient, BlobServiceClient

def sdk_config():
    CONFIG_FILE = ('config.json')
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

#---------

def upload_file2(local_file_path): #Added auto-incrementing counter to give files unique names ->filename+X
    storage_account_name = "stcontigroupone001"
    container_name = "conti-container"

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

        base_name = os.path.basename(local_file_path)
        name, ext = os.path.splitext(base_name)

        counter = 1
        existing_blobs = container_client.list_blobs(name_starts_with=name)

        for blob in existing_blobs:
            blob_name_only = os.path.splitext(os.path.basename(blob.name))[0]
            if blob_name_only.startswith(name + "_"):
                counter += 1

        blob_name = f"{name}_{counter}{ext}"


        with open(local_file_path, "rb") as data:
            container_client.upload_blob(
                name=blob_name,
                data=data,
                overwrite=False 
            )

        print(f"Uploaded '{local_file_path}' as '{blob_name}'")

    except Exception as e:
        print(f"An error occurred: {e}")

    

#---updated except
    #except Exception as e:
     #   print(f"An error occurred: {e}")
      #  return False 
    
   # return True 
