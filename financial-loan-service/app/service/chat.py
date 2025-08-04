from fastapi import File
from tempfile import TemporaryDirectory
import os
import requests


class ChatService:
    BASE_URL = os.getenv("CHAT_ENDPOINT", "http://localhost:8000/api/v1/chat/chat")

    def __init__(self, base_url=None):
        if base_url:
            self.BASE_URL = base_url

    def chat(self, session_id: str, message: str):
        data = {
            "session_id": session_id,
            "message": message
        }
        response = requests.post(self.BASE_URL, json=data)
        
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
