# app/services/classify_service.py
import json, re, logging
from string import Template
import google.generativeai as genai
from app.clients.gemini_client import GeminiClient
from app.core.config import settings
import requests

DEFAULT_TAGS = [
    ["location", "行きたい場所、泊まりたい場所など。お店の情報、ご飯屋などもここに含まれる。位置情報を持つ。位置情報を返してほしい"],
    ["train",    "時刻表など。どの駅に何時発の電車が、どの駅に何時につくかを詳細に書け。"],
    ["things",   "ほしいもの、買い物リストなど。価格や商品名、URLなどを含む"],
    ["others", "その他の情報。上記に当てはまらないもの。位置情報を持たない"],
]

PROMPT_TMPL = Template(
    """
あなたはOCRテキストの情報抽出器です。必ず **厳密なJSON** だけを返してください（前置き・コードフェンス禁止）。

■ 入力
- candidate_tags: [["<tag>","<description>"], ...]
$candidate_tags
    - 出力の "tag" フィールドは、上記 candidate_tags の **第1要素（タグ文字列）をそのまま** 1つだけ使用します。
    - **同義語・翻訳・新しい語**を作らないでください。候補に無い文字列は絶対に使わないこと。
    - どれにも当てはまらない場合は、**候補の中から最も近い説明のタグ**を1つ選びます（それでも難しければ candidate_tags の先頭を使う）。

- ocr_text:
$ocr_text

■ 出力フィールド仕様
- "status.success": trueを返すこと。
- "tag": candidate_tags の **第1要素**のいずれか **そのまま**、何も当てはまらない場合は、othersにする
- "title": OCRから短く要約したタイトル（ファイル名は使わない）
    - もしtagがthingsや商品であり、複数の商品がある場合は **商品名を半角スラッシュ "/" で連結する**
      例: "化粧水/美容液/美容オイル"
    - 商品名は短く簡潔に（名詞1〜3語程度）
    - もしtagがthingsや商品でなかったら、連結しなくてよい。**OCRから短く要約したタイトルにする**
- "location": 住所/駅/地名/URL 等の位置ヒント。GoogleMapでそのままさせるようなものがよい。無ければ ""（空文字）
- "description": 要点の短い説明（1〜2文、URL1つまで）。trainの発着情報などは詳しく載せる。無ければ ""
- "suggest_tag_title": tag が "others" の場合に、推奨される簡潔なタグ名（例: "camera", "hotel" など、英語1単語が望ましい）。それ以外は空文字 ""
- "suggest_tag_description": tag が "others" の場合に、その推奨タグの説明（例: "カメラ製品に関する記録です"）。それ以外は空文字 ""

■ 禁止事項
- JSON以外の文字、コメント、コードフェンス、例示テキストを出力しない
- "tag" に候補外の語（例: 「ご飯屋」「レストラン」など）を出さない

■ 形式（このJSONだけを返す）
{
  "results": [
    {
      "status.success": true,
      "tag": "<候補タグ>",
      "title": "<タイトル>",
      "location": "<住所等 or 空文字>",
      "description": "<説明>",
      "suggest_tag_title": "<tagがothersのときのみ、簡潔な提案タグ>",
      "suggest_tag_description": "<その説明>"
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

def get_place_from_title_location(title: str, location: str) -> dict[str, str | float] | None:
    try:
        query = f"{title} {location}".strip()
        endpoint = f"https://places.googleapis.com/v1/places:searchText?key={settings.google_maps_api_key}"
        headers = {
            "Content-Type": "application/json",
            # 返すフィールドを指定（必須）
            "X-Goog-FieldMask": "places.id,places.displayName,places.location"
        }
        payload = {"textQuery": query}

        res = requests.post(endpoint, headers=headers, json=payload, timeout=5)
        data = res.json()

        if "places" in data and data["places"]:
            place = data["places"][0]
            return {
                "lat": place["location"]["latitude"],
                "lng": place["location"]["longitude"],
                "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place['id']}",
                "maps_display_name": place.get("displayName", {}).get("text", None)
            }
        else:
            logging.warning("Places API (New) no results: %s", data)
    except Exception as e:
        logging.exception("Place Search failed: %s", e)
    return None

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
            
            # タグのバリデーション
            allowed_tags = {t[0] for t in (candidate_tags or DEFAULT_TAGS)}
            tag_val = str(item.get("tag", "")).strip()
            if tag_val not in allowed_tags:
                tag_val = "others"
                
            tagged_results = []
            for item in results:
                tag_val = str(item.get("tag", "")).strip()
                if tag_val not in allowed_tags:
                    tag_val = "others"

                location = str(item.get("location", "")).strip()
                place_info = get_place_from_title_location(item.get("title", ""), location) if location else None

                tagged_results.append({
                    "status.success": bool(item.get("status.success", False)),
                    "tag": tag_val,
                    "title": item.get("title", ""),
                    "location": location,
                    "description": item.get("description", ""),
                    "lat": place_info["lat"] if place_info else None,
                    "lng": place_info["lng"] if place_info else None,
                    "maps_url": place_info["maps_url"] if place_info else None,
                    "maps_display_name": place_info["maps_display_name"] if place_info else None,
                    "suggest_tag_title": item.get("suggest_tag_title", "") if tag_val == "others" else "",
                    "suggest_tag_description": item.get("suggest_tag_description", "") if tag_val == "others" else ""
                })

            return {"results": tagged_results}
        except Exception as e:
            logging.warning("[Gemini] normalize failed: %s", e)
            return _fallback_from_ocr(ocr_text, candidate_tags or DEFAULT_TAGS)
