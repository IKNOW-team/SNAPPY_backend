import google.generativeai as genai
from app.core.config import settings

class GeminiClient:
    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        genai.configure(api_key=api_key or settings.gemini_api_key)
        self._model = genai.GenerativeModel(model_name=model_name or settings.gemini_model_name)

    @property
    def model(self):
        return self._model

# DI 用のシングルトン・ファクトリ
_gemini: GeminiClient | None = None

def get_gemini_client() -> GeminiClient:
    global _gemini
    if _gemini is None:
        _gemini = GeminiClient()
    return _gemini