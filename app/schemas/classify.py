from pydantic import BaseModel

class ClassifyResponse(BaseModel):
    ocr_text: str
    classification: str
    
class BatchClassifyItem(BaseModel):
    filename: str
    ok: bool
    ocr_text: str | None = None
    classification: str | None = None
    error: str | None = None

class BatchClassifyResponse(BaseModel):
    results: list[BatchClassifyItem]