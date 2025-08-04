import asyncio
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
import os

class GoogleCloudStorageWrapper:
    def __init__(self, bucket_name: str):
        self.client = storage.Client(project=os.getenv("PROJECT_ID"))
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, source_file_path: str, destination_blob_name: str):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)

    def download_file(self, source_blob_name: str, destination_file_path: str):
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)

    def download_file_as_bytes(self, source_blob_name: str) -> bytes:
        blob = self.bucket.blob(source_blob_name)
        return blob.download_as_bytes()

    def delete_file(self, blob_name: str):
        blob = self.bucket.blob(blob_name)
        blob.delete()

    def list_files(self, prefix: str = None):
        blobs = list(self.bucket.list_blobs(prefix=prefix))
        return [blob.name for blob in blobs]

    def upload_from_string(self, data: str, destination_blob_name: str, content_type: str ='text/plain'):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(data=data, content_type=content_type)

    def is_file_exists(self, blob_name: str) -> bool:
        blob = self.bucket.blob(blob_name)
        return blob.exists()
