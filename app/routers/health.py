from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(message="It works!")

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(message="ok")