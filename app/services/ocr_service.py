from google.cloud import vision
from app.utils.file_loader import read_bytes

class OCRService:
    def __init__(self, client: vision.ImageAnnotatorClient) -> None:
        self.client = client

    def run_ocr(self, file_path: str) -> str:
        content = read_bytes(file_path)
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        if not texts:
            return ""
        return texts[0].description
        
    def run_ocr_bytes(self, data: bytes) -> str:
        image = vision.Image(content=data)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        if not texts:
            return ""
        return texts[0].description
        
        