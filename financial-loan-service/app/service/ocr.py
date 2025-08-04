import asyncio
from google.cloud import vision
from concurrent.futures import ThreadPoolExecutor

 
class OCRService:
    def __init__(self, 
                    mime_type: str = "application/pdf", 
                    batch_size: int = 2) -> None:
        self.client = vision.ImageAnnotatorClient()
        self.mime_type = mime_type
        self.batch_size = batch_size
        self.feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
        self.executor = ThreadPoolExecutor()
  
       
    def analyze_image(self, bucket_name: str, source_file: str, destination_path: str) -> dict:
        """Analyze the image using Google Cloud Vision API."""
        uri_source = f"gs://{bucket_name}/{source_file}"
        uri_destination = f"gs://{bucket_name}/{destination_path}"
        gcs_source = vision.GcsSource(uri=uri_source)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=self.mime_type)
        gcs_destination = vision.GcsDestination(uri=uri_destination)
        output_config = vision.OutputConfig(
            gcs_destination=gcs_destination, batch_size=self.batch_size
        )
        async_request = vision.AsyncAnnotateFileRequest(
            features=[self.feature], input_config=input_config, output_config=output_config
        )

        request = vision.AsyncBatchAnnotateFilesRequest(
            requests=[async_request]
            )

        
        operation = self.client.async_batch_annotate_files(request=request)

        return operation.result(timeout=240)
    