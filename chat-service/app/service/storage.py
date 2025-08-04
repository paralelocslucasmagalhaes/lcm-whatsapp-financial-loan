import asyncio
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
import os

class GoogleCloudStorageWrapper:
    def __init__(self, bucket_name: str):
        self.client = storage.Client(project=os.getenv("PROJECT_ID"))
        self.bucket = self.client.bucket(bucket_name)
        self.executor = ThreadPoolExecutor()

    async def upload_file(self, source_file_path: str, destination_blob_name: str):
        loop = asyncio.get_running_loop()
        blob = self.bucket.blob(destination_blob_name)
        await loop.run_in_executor(self.executor, blob.upload_from_filename, source_file_path)

    async def download_file(self, source_blob_name: str, destination_file_path: str):
        loop = asyncio.get_running_loop()
        blob = self.bucket.blob(source_blob_name)
        await loop.run_in_executor(self.executor, blob.download_to_filename, destination_file_path)

    async def delete_file(self, blob_name: str):
        loop = asyncio.get_running_loop()
        blob = self.bucket.blob(blob_name)
        await loop.run_in_executor(self.executor, blob.delete)

    async def list_files(self, prefix: str = None):
        loop = asyncio.get_running_loop()
        blobs = await loop.run_in_executor(self.executor, lambda: list(self.bucket.list_blobs(prefix=prefix)))
        return [blob.name for blob in blobs]