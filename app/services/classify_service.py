from app.clients.gemini_client import GeminiClient

PROMPT_TMPL = (
    """
あなたはOCR後テキストの情報抽出器である。以下の入力を受け取り、指定のスキーマでのみJSONを返す。

## 入力
- candidate_tags: 二次元配列。各要素は [tag, description]。ここから最も適切な tag を一つだけ選ぶ。
{candidate_tags}

- ocr_text: 画像からOCRした生テキスト。改行・ノイズを含む。
""
{ocr_text}
""

## やること
1) ocr_text を軽く正規化（全角/半角や余分な改行を整理）したうえで内容を把握。
2) candidate_tags の説明と照合し、最も適合する tag を一つ選ぶ。
   - 例: 位置・宿・観光 → "location"、時刻表・乗換 → "train"、商品名・価格・URL → "things"
   - どれも弱い場合は、意味が最も近いものを一つ選ぶ（必ず候補内から選ぶ）。
3) 以下の項目を抽出:
   - title: 店名/スポット名/商品名/路線・列車名など、要点を10〜30文字程度で。
   - location: 住所、駅名、施設名、URL内の地名など位置を示す情報があれば短く。なければ空文字 ""。
   - description: 画像（テキスト）から分かる要点を一文〜二文で要約。URL等があれば1つだけ含めてよい。
4) 正しく抽出できたら status.success=true。主要項目が空しか得られない場合は false。

## 出力フォーマット
以下のJSONのみを返す。余計な文章は禁止。キー順はこの通り。
{
  "results": [
    {
      "status.success": <true|false>,
      "tag": "<candidate_tags 内のどれかを1つ>",
      "title": "<文字列>",
      "location": "<文字列または空文字>",
      "description": "<文字列または空文字>"
    }
  ]
}

## 制約
- 出力は厳格に上記JSONのみ。説明文・推論過程・追加キーは禁止。
- 幻覚で新情報を作らない。URL/住所はOCRに存在するものだけ。
- 絵文字・装飾・改行コードは使わない。

"""
).strip()

class ClassifyService:
    def __init__(self, gemini: GeminiClient) -> None:
        self.gemini = gemini
        
    def classify(self, ocr_text: str) -> str:
        prompt = PROMPT_TMPL.format(candidate_tags="[]", ocr_text=ocr_text or "")
        result = self.gemini.model.generate_content(prompt)
        return (result.text or "").strip()

    def classify_with_tags(self, ocr_text: str, candidate_tags: list[list[str]]) -> str:
        # candidate_tags をそのまま文字列に埋め込む（JSONにするのが安全）
        import json
        tags_str = json.dumps(candidate_tags, ensure_ascii=False)
        prompt = PROMPT_TMPL.replace("{candidate_tags}", tags_str).replace("{ocr_text}", ocr_text or "")
        res = self.gemini.model.generate_content(prompt)
        return (res.text or "").strip()