from azure.storage.blob import BlobServiceClient

from src import Config


def create_blob_storage_context() -> BlobServiceClient:
    blob_storage_context = BlobServiceClient.from_connection_string(Config.AZURE_STORAGE_ACCOUNT_CONNECTION_STRING)
    return blob_storage_context
