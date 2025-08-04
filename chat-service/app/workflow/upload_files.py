
from typing import Dict
from service.storage import GoogleCloudStorageWrapper
from fastapi import  File

from tempfile import TemporaryDirectory
import os

class HandleFiles:

    def __init__(self, user: str):
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.user = user

    async def upload_file_to_bucket(self, file: File) -> str:
        file_path = file.filename.split(".")[0]
        destination_path = f"bills/{self.user}/{file_path}"
                
        storage = GoogleCloudStorageWrapper(self.bucket_name)

        # Save the uploaded file to a temporary directory
        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)

            # Upload the file to Google Cloud Storage
            await storage.upload_file(file_path, f"{destination_path}/{file.filename}")
        return {
                "bucket_name": self.bucket_name, 
                "destination_file": destination_path,
                "uri": f"gs://{self.bucket_name}/{destination_path}/{file.filename}"
            }
    
    async def upload_twilio_file_to_bucket(self, filepath: str) -> str:
        filename = filepath.split("/")[-1]
        file_path = filename.split(".")[0]
        destination_path = f"bills/{self.user}/{file_path}"
                
        storage = GoogleCloudStorageWrapper(self.bucket_name)
        # Upload the file to Google Cloud Storage
        await storage.upload_file(filepath, f"{destination_path}/{filename}")
        return {
                "bucket_name": self.bucket_name, 
                "destination_file": destination_path,
                "uri": f"gs://{self.bucket_name}/{destination_path}/{filename}"
            }