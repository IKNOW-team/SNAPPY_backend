# Imports the Google Cloud client library
from google.cloud import vision
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai
import os

# .env を読み込む（プロジェクトルートに .env がある前提）
load_dotenv()

# Gemini API設定（Gemini 2.0 Flashを明示的に指定）
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Vision用認証キーのパスを環境変数にセット（Googleが自動検出）
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


app = FastAPI()

@app.get("/")
def root():
    return {"message": "It works!"}

@app.get("/quickstart")
def run_quickstart():
    # Vision APIクライアント
    client = vision.ImageAnnotatorClient()

    # ローカル画像のパス（FastAPIプロジェクト内にあると仮定）
    file_path = "static/image3.jpg"  # 自分の画像のパスに変更

    # 画像をバイナリ読み込み
    with open(file_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # ラベル検出
    response = client.label_detection(image=image)
    labels = response.label_annotations

    print("Labels:")
    for label in labels:
        print(label.description)

    return {
        "labels": [label.description for label in labels]
    }
    

@app.get("/ocr")
def run_ocr():
    # Cloud Vision API クライアントの初期化
    client = vision.ImageAnnotatorClient()

    # ローカル画像のパス（自分の画像ファイルに合わせて変更）
    file_path = "static/image1.jpg"

    # 画像をバイナリで読み込む
    with open(file_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # OCR（テキスト検出）を実行
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return {"text": "", "message": "No text detected"}

    # 最初の要素に全体の検出結果が入っている（複数行含む）
    full_text = texts[0].description

    return {
        "text": full_text
    }
    
@app.get("/ocr-and-classify")
def ocr_and_classify():
    file_path = "static/image1.jpg"

    # OCR
    with open(file_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return {"text": "", "message": "No text detected"}

    ocr_text = texts[0].description

    # Geminiプロンプト
    prompt = f"""
以下は、OCRで読み取った内容です。以下の情報を抽出してください：

1. ジャンル（ご飯屋 / 観光地 / 本 / 乗り換え案内 / その他）
2. タイトル（店名・本の名前など）
3. 場所（住所・市区町村・駅名など）
4. 備考（価格・営業時間・感想などがあれば）

### OCRテキスト：
{ocr_text}
"""

    result = model.generate_content(prompt)
    return {
        "ocr_text": ocr_text,
        "classification": result.text
    }