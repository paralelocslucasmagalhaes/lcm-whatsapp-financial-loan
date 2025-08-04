from fastapi import APIRouter

from api.v1.endpoints import extract_bill



api_router = APIRouter()
api_router.include_router(extract_bill.router, prefix="/extract-bill-info", tags=["Bill Extraction"])
