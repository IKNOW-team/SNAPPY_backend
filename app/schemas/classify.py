from pydantic import BaseModel, Field
from typing import List, Literal, Optional

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
    
class TaggedItem(BaseModel):
    status_success: bool = Field(..., alias="status.success")
    tag: str
    title: str
    location: str
    description: str

class TaggedBatchResponse(BaseModel):
    results: List[TaggedItem]