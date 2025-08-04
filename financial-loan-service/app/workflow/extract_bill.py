
from typing import Dict
from service.vertex import VertexAIService
from service.storage import GoogleCloudStorageWrapper
from service.ocr import OCRService  # Assuming you have a VisionAPI service for OCR extraction
from fastapi import UploadFile, File
from service.chat import ChatService

from tempfile import TemporaryDirectory
import os
import json
import logging
import asyncio
from time import sleep

class ExtractBill:

    def __init__(self, user: str):
        self.vertex_ai = VertexAIService()
        self.bucket_name = os.getenv("BUCKET_NAME", "lcm-solfacil-financiamento-bills")
        self.user = user
        self.ocr_service = OCRService(mime_type="application/pdf", batch_size=1)
        self.storage = GoogleCloudStorageWrapper(self.bucket_name)
        self.chat_service = ChatService()

    # -- upload the file to bucket
    # -- extract the OCR with vision API
    # -- use Vertex AI to extract bill information

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
                "destination_file": destination_path
            }

    def read_ocr_from_bucket(self, source_path) -> str:        
        storage_files = self.storage.list_files(prefix=source_path)
        content = ""
        with TemporaryDirectory() as temp_dir:
            for file in storage_files:
                if not file.endswith('.json'):
                    continue
                # Download the file to a temporary location
                file_path = os.path.join(temp_dir, file.split('/')[-1])
                self.storage.download_file(file, file_path)
                # Read the OCR content
                with open(file_path, 'r') as f:
                    ocr_content = json.load(f)
                full_text = self.get_full_text_from_ocr(ocr_content)
                content = content + full_text + "\n"
                
        return content
    
    def get_full_text_from_ocr(self, ocr_content: Dict) -> str:
        """Extract full text from OCR content."""
        full_text = ""
        for page in ocr_content.get('responses', []):
            if 'fullTextAnnotation' in page:
                full_text += page['fullTextAnnotation'].get('text', '')
        return full_text
    
    def clean_llm_json(self, response:str):
        # Remove Markdown code fences
        if response.startswith("```"):
            response = response[len("```json"):]
        return response.strip().strip('```')
        

    def extract_ocr_from_bill(self, filename) -> Dict:
        file_path = filename.split(".")[0]
        destination_path = f"bills/{self.user}/{file_path}"
        vision_destination_path = f"{destination_path}/vision/"
        
        # Upload the file to Google Cloud Storage
        # await self.upload_file_to_bucket(file, destination_path)

        # Extract OCR with Vision API
        ocr_uri_destination = self.ocr_service.analyze_image(bucket_name=self.bucket_name, 
                                                                    source_file=f"{destination_path}/{filename}", 
                                                                    destination_path=vision_destination_path)
        
        while not self.is_ocr_extracted(vision_destination_path):
            logging.warning("Waiting for OCR extraction to complete...")
            sleep(2)
        
        # Use Vertex AI to extract bill information
        ocr_content = self.read_ocr_from_bucket(vision_destination_path)

        logging.warning(f"OCR content: {len(ocr_content)}")
        extracted_info = self.vertex_ai.ask(ocr_content)       

        logging.warning(f"Extracted info: {extracted_info}")

        llm_response = self.clean_llm_json(extracted_info)

        self.storage.upload_from_string(
            data=llm_response, 
            destination_blob_name=f"{destination_path}/extracted_info.json", 
            content_type='application/json'
        )

        self.chat_service.chat(session_id=self.user, message="Notifying user about the extraction completion and call the tool status bill extraction")

        return json.loads(llm_response)
    
    def is_ocr_extracted(self, vision_destination_path) -> bool:
                
        storage_files = self.storage.list_files(prefix=vision_destination_path)
        
        for file in storage_files:
            if not file.endswith('.json'):
                continue
            return True
                
        return False
    
    def is_llm_extracted(self, llm_destination_path) -> bool:
                
        return self.storage.is_file_exists(blob_name=llm_destination_path)    

    def get_llm_extracted(self, llm_path: str ) -> bool:
    
        # with TemporaryDirectory() as temp_dir:
        #     file_path = os.path.join(temp_dir, "extracted_info.json")
        #     self.storage.download_file(llm_path, file_path)
        #     with open(file_path, 'r') as f:
        #         return json.load(f)
        llm_file = self.storage.download_file_as_bytes(llm_path)
        return json.loads(llm_file) if llm_file else {}
    
    def check_status(self, filename, event) -> Dict:
        file_path = filename.split(".")[0]
        destination_path = f"bills/{self.user}/{file_path}"
        llm_destination_path = f"{destination_path}/extracted_info.json"
        
        if event == "extract":
            if self.is_llm_extracted(llm_destination_path):
                llm_extracted = self.get_llm_extracted(llm_destination_path)
                return {
                    "status": "success",
                    "result": llm_extracted
                }
            else:
                return {
                    "status": "pending",
                    "result": {}
                }
            