from fastapi import APIRouter, status, Request
import logging
from typing import Dict, Optional
from fastapi import File, UploadFile, Form
from service.chat import ChatService
import os
import uuid
from workflow.upload_files import HandleFiles
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from tempfile import TemporaryDirectory
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from schemas.schemas import RequestChat

router = APIRouter()

@router.post("", status_code=status.HTTP_200_OK)
async def dialogflow_interaction(
    session_id: str = Form(...),
    message: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
) -> Dict:
    
    # Import Dialogflow client
    # session_id = str(uuid.uuid4()) if not session_id else session_id
    handle_file = HandleFiles(user=session_id)
    file_uri = ""
    if file:
        
        # Upload the file to Google Cloud Storage
        bucket_info = await handle_file.upload_file_to_bucket(file)
        # Use the filename for Dialogflow interaction
        file_uri = bucket_info.get("uri")
        message = message + '\n' + f"File uploaded: {file_uri}. Please process this file."
    chat_service = ChatService()
    #
    # Extract response text
    fulfillment_text = chat_service.get_answer(user=session_id, user_message=message, file=file_uri)

    return {"response": fulfillment_text}


@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def whatsapp(MessageSid: str = Form(...), 
                AccountSid: str = Form(...), 
                NumMedia: str = Form(...),
                From: str = Form(...), 
                Body: str = Form(...), 
                To: str = Form(...),
                MediaUrl0: Optional[str] = Form(None),
                MediaContentType0: Optional[str] = Form(None)
        ):
    
    session_user = From.split(":")[-1]  # Extract the user from the From field
    session_user = session_user.replace("+", "").strip()  # Clean up the user identifier
    handle_file = HandleFiles(user=session_user)
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    file_uri = ""
    client = Client(account_sid, auth_token)
    if int(NumMedia) > 0:
        # If there is media, we can process it
        media_url = MediaUrl0
        media_name = media_url.split("/")[-1]
        media_content_type = MediaContentType0.split("/")[-1]
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            executor, 
            lambda: requests.get(media_url, auth=(account_sid, auth_token))
        )
        content_disposition = response.headers.get("content-disposition")
        with TemporaryDirectory() as temp_dir:
            media_path = os.path.join(temp_dir, f"{media_name}.{media_content_type}")
            with open(media_path, "wb") as f:
                f.write(response.content)
            bucket_info = await handle_file.upload_twilio_file_to_bucket(media_path)
            file_uri = bucket_info.get("uri")
            Body = Body + '\n' + f"File uploaded: {file_uri}. Please process this file."
    
    logging.warning(f"Request payload: {From}")

    chat_service = ChatService()
    #
    # Extract response text
    fulfillment_text = chat_service.get_answer(user=session_user, user_message=Body, file=file_uri)
    twilio_message = client.messages.create(
        body=fulfillment_text[0],
        from_=To,
        to=From
    )
    # response_message = MessagingResponse()
    # response_message.message(fulfillment_text[0])
    # Get raw bytes
    # raw_body = await request.body()
    # Parse as JSON (if JSON)
    logging.warning(f"Request Body payload: {Body}")
    logging.warning(f"Request Body payload: {fulfillment_text[0]}")
    return str(twilio_message)
   



@router.post("/chat", status_code=status.HTTP_200_OK)
async def dialogflow_chat_interaction(
    payload: RequestChat
) -> Dict:
    
    # Import Dialogflow client
    # session_id = str(uuid.uuid4()) if not session_id else session_id    
    chat_service = ChatService()
    #
    # Extract response text
    fulfillment_text = chat_service.get_answer(user=payload.session_id, user_message=payload.message, file=None)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
    client = Client(account_sid, auth_token)
    twilio_message = client.messages.create(
        body=fulfillment_text[0],
        from_=twilio_from_number,
        to=f"whatsapp:+{payload.session_id}"
    )

    return {"response": fulfillment_text}