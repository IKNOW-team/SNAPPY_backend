from google.cloud import vision

class VisionClient:
    def __init__(self) -> None:
        self._client = vision.ImageAnnotatorClient()

    @property
    def client(self) -> vision.ImageAnnotatorClient:
        return self._client

_vision: VisionClient | None = None

def get_vision_client() -> VisionClient:
    global _vision
    if _vision is None:
        _vision = VisionClient()
    return _vision