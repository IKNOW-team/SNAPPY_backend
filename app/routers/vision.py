from fastapi import APIRouter, Depends, HTTPException
from app.clients.vision_client import get_vision_client, VisionClient
from app.services.label_service import LabelService

router = APIRouter(prefix="/vision", tags=["vision"])

@router.get("/labels")
async def detect_labels(file_path: str = "static/image3.jpg", vc: VisionClient = Depends(get_vision_client)):
    try:
        service = LabelService(vc.client)
        labels = service.detect_labels(file_path)
        return {"labels": labels}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")