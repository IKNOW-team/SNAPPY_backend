from pydantic import BaseModel, Field

class OCRRequest(BaseModel):
    # 将来: ファイルアップロードやURL対応に拡張
    file_path: str = Field(..., description="ローカル画像パス")

class OCRResponse(BaseModel):
    text: str
    message: str | None = None