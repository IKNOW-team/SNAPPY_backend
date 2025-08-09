from app.clients.gemini_client import GeminiClient

PROMPT_TMPL = (
    """
以下はOCRで読み取った内容です。以下の情報を抽出してください：

1. ジャンル（ご飯屋 / 観光地 / 本 / 乗り換え案内 / その他）
2. タイトル（店名・本の名前など）
3. 場所（住所・市区町村・駅名など）
4. 備考（価格・営業時間・感想などがあれば）

### OCRテキスト：
{ocr_text}
"""
).strip()

class ClassifyService:
    def __init__(self, gemini: GeminiClient) -> None:
        self.gemini = gemini

    def classify(self, ocr_text: str) -> str:
        prompt = PROMPT_TMPL.format(ocr_text=ocr_text)
        result = self.gemini.model.generate_content(prompt)
        return result.text or ""