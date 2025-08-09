# app/services/classify_service.py
import json, re, logging
from string import Template
import google.generativeai as genai
from app.clients.gemini_client import GeminiClient

DEFAULT_TAGS = [
    ["location", "行きたい場所、泊まりたい場所など。位置情報を持つ。位置情報を返してほしい"],
    ["train",    "時刻表など。どの駅に何時発の電車が、どの駅に何時につくか"],
    ["things",   "ほしいもの"],
]

PROMPT_TMPL = Template(
    """
以下はOCRで読み取った内容です。以下の情報を抽出してください：

1. ジャンル（ご飯屋 / 観光地 / 本 / 乗り換え案内 / その他）
2. タイトル（店名・本の名前など）
3. 場所（住所・市区町村・駅名など）
4. 備考（価格・営業時間・感想などがあれば）

※ 出力は **厳密なJSON**。前置き・コードフェンスは禁止。
※ title は必ず OCR から抽出（ファイル名は使わない）。

候補タグ:
$candidate_tags

### OCRテキスト：
$ocr_text

出力（このJSONのみ）:
{
  "results": [
    {
      "status.success": true,
      "tag": "<候補タグの中から1つ>",
      "title": "<OCRから抽出した短いタイトル>",
      "location": "<住所/駅/地名/URLなど。無ければ空文字>",
      "description": "<要点の短い説明（1〜2文以内）。無ければ空文字>"
    }
  ]
}
""".strip()
)

def _strip_code_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.DOTALL)
    return s.strip()

def _extract_json_object(s: str) -> str | None:
    s2 = _strip_code_fence(s.strip())
    try:
        json.loads(s2); return s2
    except Exception:
        pass
    start=-1; depth=0; in_str=False; esc=False
    for i,ch in enumerate(s2):
        if in_str:
            if esc: esc=False
            elif ch == '\\': esc=True
            elif ch == '"': in_str=False
            continue
        if ch == '"': in_str=True; continue
        if ch == '{':
            if depth==0: start=i
            depth+=1
        elif ch == '}':
            if depth>0:
                depth-=1
                if depth==0 and start!=-1:
                    return s2[start:i+1]
    return None

def _fallback_from_ocr(ocr_text: str, candidate_tags: list[list[str]]) -> dict:
    t = (ocr_text or "").strip()
    # タイトル（OCRから抽出）
    title = ""
    for line in t.splitlines():
        s=line.strip()
        if not s: continue
        if re.match(r"^(https?://|www\.)", s): continue
        if re.match(r"^\d{1,2}:\d{2}$", s): continue
        if len(s) < 3: continue
        title = s[:40]; break
    if not title: title = (t[:40] or "Untitled")
    # 位置
    location=""
    m=re.search(r"(?:[^\s　]+駅|[^\s　]+市|[^\s　]+区|[^\s　]+町|[^\s　]+村)", t)
    if m: location=m.group(0)[:40]
    else:
        u=re.search(r"(https?://[^\s]+)", t)
        if u: location=u.group(1)[:80]
    # タグ推定（候補内から）
    tag = candidate_tags[0][0] if candidate_tags else "location"
    if re.search(r"\d{1,2}:\d{2}|navitime|jr|発|着|train", t, re.I): tag="train"
    elif re.search(r"¥|\$|価格|税込|円|amazon|rakuten|mercari", t): tag="things"
    elif re.search(r"駅|市|区|町|村|hotel|inn|maps|google\.com/maps", t, re.I): tag="location"
    # 説明
    lines=[l.strip() for l in t.splitlines() if l.strip()][:2]
    desc=(f"候補タグ: {tag}。位置ヒント: {location}" if location else " / ".join(lines)[:120])

    return {"results":[{
        "status.success": False,
        "tag": tag,
        "title": title,
        "location": location,
        "description": desc
    }]}

class ClassifyService:
    def __init__(self, gemini: GeminiClient) -> None:
        self.gemini = gemini
        self._genconf = genai.types.GenerationConfig(
            temperature=0.2,
            top_p=0.8,
            response_mime_type="application/json",
        )

    def classify_json_with_tags(self, ocr_text: str, candidate_tags: list[list[str]] = DEFAULT_TAGS) -> dict:
        """候補タグを使って厳密JSONで返す。失敗時も同スキーマでフォールバック。"""
        safe_ocr_text = (ocr_text or "").replace("$", "$$")
        tags_str = json.dumps(candidate_tags or DEFAULT_TAGS, ensure_ascii=False)
        prompt = PROMPT_TMPL.substitute(ocr_text=safe_ocr_text, candidate_tags=tags_str)

        try:
            res = self.gemini.model.generate_content(prompt, generation_config=self._genconf)
        except Exception as e:
            logging.exception("Gemini generate_content error")
            return _fallback_from_ocr(ocr_text, candidate_tags or DEFAULT_TAGS)

        raw = (getattr(res, "text", None) or "").strip()
        if not raw:
            fb = getattr(res, "prompt_feedback", None)
            logging.warning("[Gemini] empty text. feedback=%s", getattr(fb, "block_reason", None))
            return _fallback_from_ocr(ocr_text, candidate_tags or DEFAULT_TAGS)

        # JSONとして頑丈に解釈
        try:
            payload = json.loads(_strip_code_fence(raw))
        except Exception:
            block = _extract_json_object(raw)
            if not block:
                return _fallback_from_ocr(ocr_text, candidate_tags or DEFAULT_TAGS)
            try:
                payload = json.loads(block)
            except Exception:
                return _fallback_from_ocr(ocr_text, candidate_tags or DEFAULT_TAGS)

        # 最終正規化
        try:
            results = payload.get("results")
            if not isinstance(results, list) or not results or not isinstance(results[0], dict):
                raise ValueError("results missing")
            item = results[0]
            return {
                "results": [{
                    "status.success": bool(item.get("status.success", False)),
                    "tag": str(item.get("tag", "")),
                    "title": str(item.get("title", "")),
                    "location": str(item.get("location", "")),
                    "description": str(item.get("description", "")),
                }]
            }
        except Exception as e:
            logging.warning("[Gemini] normalize failed: %s", e)
            return _fallback_from_ocr(ocr_text, candidate_tags or DEFAULT_TAGS)
