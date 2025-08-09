from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.clients.vision_client import get_vision_client, VisionClient
from app.clients.gemini_client import get_gemini_client, GeminiClient
from app.schemas.ocr import OCRResponse
from app.schemas.classify import ClassifyResponse, BatchClassifyItem, BatchClassifyResponse
from app.services.ocr_service import OCRService
from app.services.classify_service import ClassifyService
from app.utils.validators import is_mime_allowed, read_limited, MAX_BYTES
from app.core.config import settings
from app.utils.threads import run_sync, bounded_gather

router = APIRouter(prefix="/ocr", tags=["ocr"])

@router.get("/text", response_model=OCRResponse)
async def run_ocr(file_path: str = "static/image1.jpg", vc: VisionClient = Depends(get_vision_client)):
    try:
        ocr = OCRService(vc.client)
        text = ocr.run_ocr(file_path)
        if not text:
            return OCRResponse(text="", message="No text detected")
        return OCRResponse(text=text)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/text-and-classify", response_model=ClassifyResponse)
async def ocr_and_classify(file_path: str = "static/image1.jpg",
                           vc: VisionClient = Depends(get_vision_client),
                           gc: GeminiClient = Depends(get_gemini_client)):
    try:
        ocr = OCRService(vc.client)
        text = ocr.run_ocr(file_path)
        classifier = ClassifyService(gc)
        classification = classifier.classify(text)
        return ClassifyResponse(ocr_text=text, classification=classification)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
      
@router.post("/upload-and-classify", response_model=ClassifyResponse, status_code=status.HTTP_200_OK)
async def upload_and_classify(file: UploadFile = File(...),
                              vc: VisionClient = Depends(get_vision_client),
                              gc: GeminiClient = Depends(get_gemini_client)):
    # validate file type
    if not (file.content_type and file.content_type.startswith("image/")):
        raise HTTPException(status_code=415, detail="Unsupported Media Type: expected image/*")

    # load file data
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    # OCR → classification
    ocr = OCRService(vc.client)
    text = ocr.run_ocr_bytes(data)
    classifier = ClassifyService(gc)
    classification = classifier.classify(text)

    return ClassifyResponse(ocr_text=text, classification=classification)
  
@router.post(
    "/upload-and-classify-batch",
    response_model=BatchClassifyResponse,
    status_code=status.HTTP_200_OK
)
async def upload_and_classify_batch(
    files: List[UploadFile] = File(..., description="画像ファイルを複数"),
    vc: VisionClient = Depends(get_vision_client),
    gc: GeminiClient = Depends(get_gemini_client),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # file limit
    MAX_FILES = 16
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=413, detail=f"Too many files (>{MAX_FILES})")

    ocr = OCRService(vc.client)
    classifier = ClassifyService(gc)

    results: list[BatchClassifyItem] = []

    for f in files:
        name = f.filename or "unnamed"
        # MIME check
        if not (f.content_type and f.content_type.startswith("image/")) or f.content_type == "image/svg+xml":
            results.append(BatchClassifyItem(
                filename=name, ok=False, error=f"Unsupported Media Type: {f.content_type}"
            ))
            continue

        data = await f.read()
        if not data:
            results.append(BatchClassifyItem(filename=name, ok=False, error="Empty file"))
            continue

        try:
            text = ocr.run_ocr_bytes(data)
            classification = classifier.classify(text)
            results.append(BatchClassifyItem(
                filename=name, ok=True, ocr_text=text, classification=classification
            ))
        except Exception as e:
            results.append(BatchClassifyItem(
                filename=name, ok=False, error=str(e)
            ))

    return BatchClassifyResponse(results=results)
  