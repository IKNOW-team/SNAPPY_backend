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
    lat: Optional[float] = None
    lng: Optional[float] = None
    maps_url: Optional[str] = None
    maps_display_name: Optional[str] = None
    suggest_tag_title: Optional[str] = None
    suggest_tag_description: Optional[str] = None

class TaggedResponse(BaseModel):
    results: List[TaggedItem]