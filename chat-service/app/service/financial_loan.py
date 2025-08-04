import aiohttp
from fastapi import File
from tempfile import TemporaryDirectory
import os


class FinancialLoanService:
    BASE_URL = "https://teste.com.br/api/v1/extract"

    def __init__(self, base_url=None):
        if base_url:
            self.BASE_URL = base_url

    async def get(self, params=None, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
            
    async def post_json(self, json_data=None, params=None, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL, json=json_data, params=params, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
            
    async def post_data(self, data=None, params=None, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL, data=data, params=params, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
            
    async def upload_bill(self, file: File):
        data = aiohttp.FormData()
        with TemporaryDirectory as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            data.add_field('file',
                            open(file_path, 'rb'),
                            filename=file.filename,
                            content_type=file.content_type)
            
            return await self.post_data(data=data)
       