from fastapi import APIRouter, status

from typing import Dict
from fastapi import File, UploadFile, Form, BackgroundTasks
from schemas.schemas import RequestExtractOcr, RequestCheckStatus
from workflow.extract_bill import ExtractBill

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    user: str = Form(...),
    file: UploadFile = File(...)
) -> Dict:
    
    bill = ExtractBill(user=user)
    # Process the uploaded file here
    bucket = await bill.upload_file_to_bucket(file)
    # Example: just return the filename and size
    return {
        "filename": file.filename,
        "bucket_name": bucket.get("bucket_name"),
        "destination": bucket.get("destination_file")
    }

@router.post("/extract", status_code=status.HTTP_202_ACCEPTED)
async def extract_ocr(payload: RequestExtractOcr, background_tasks: BackgroundTasks) -> Dict:
    
    bill = ExtractBill(user=payload.user)
    file = payload.uri.split("/")[-1] 
    # Process the uploaded file here
    # Example: just return the filename and size
    background_tasks.add_task(bill.extract_ocr_from_bill, file)
    return {"message": "OCR extraction started in the background."}

@router.post("/status", status_code=status.HTTP_200_OK)
async def check_status(payload: RequestCheckStatus) -> Dict:

    bill = ExtractBill(user=payload.user)
    file = payload.uri.split("/")[-1] 
    # Process the uploaded file here
    # Example: just return the filename and size
    return bill.check_status(filename=file, event=payload.event)