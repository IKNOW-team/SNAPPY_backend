from google.cloud import vision
from app.utils.file_loader import read_bytes

class LabelService:
    def __init__(self, client: vision.ImageAnnotatorClient) -> None:
        self.client = client

    def detect_labels(self, file_path: str) -> list[str]:
        content = read_bytes(file_path)
        image = vision.Image(content=content)
        response = self.client.label_detection(image=image)
        return [label.description for label in response.label_annotations]