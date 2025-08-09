# SNAPPY Backend

Google Cloud Vision API と Gemini AI を使用した OCR・画像分析 API サーバー

## 概要

このプロジェクトは、画像からテキストを抽出し、AI による自動分類を行う FastAPI ベースの WebAPI です。主に以下の機能を提供します：

- 画像のラベル検出
- OCR によるテキスト抽出
- OCR 結果の AI 分析・分類

## 技術スタック

- **Python 3.10**
- **FastAPI** - WebAPI フレームワーク
- **Google Cloud Vision API** - OCR・画像解析
- **Google Gemini AI** - テキスト分析・分類
- **Docker** - コンテナ化
- **Uvicorn** - ASGI サーバー

## 機能

### API エンドポイント

| エンドポイント          | 説明           | 機能                                   |
| ----------------------- | -------------- | -------------------------------------- |
| `GET /`                 | ヘルスチェック | サーバーの動作確認                     |
| `GET /quickstart`       | ラベル検出     | 画像内のオブジェクトを検出・ラベル付け |
| `GET /ocr`              | OCR            | 画像からテキストを抽出                 |
| `GET /ocr-and-classify` | OCR + AI 分析  | テキスト抽出 + AI による情報分類       |

### AI 分類機能

`/ocr-and-classify` エンドポイントでは、OCR で抽出されたテキストを以下のカテゴリで自動分類します：

1. **ジャンル**: ご飯屋 / 観光地 / 本 / 乗り換え案内 / その他
2. **タイトル**: 店名・本の名前など
3. **場所**: 住所・市区町村・駅名など
4. **備考**: 価格・営業時間・感想など

## セットアップ

### 前提条件

- Docker & Docker Compose
- Google Cloud Platform アカウント
- Google Gemini API キー

### 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下の環境変数を設定してください：

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=./vision-key.json
```

### Google Cloud 認証設定

1. Google Cloud Console で Vision API を有効化
2. サービスアカウントキーを作成し、`vision-key.json` として保存
3. プロジェクトルートに配置

### Docker を使用した起動

```bash
# リポジトリのクローン
git clone <repository-url>
cd giiku

# 環境変数ファイルの作成
cp .env.example .env
# .env ファイルを編集して API キーを設定

# Docker Compose で起動
docker-compose up --build
```

### ローカル開発環境

```bash
# 依存関係のインストール
pip install -r requirements.txt

# サーバー起動
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## 使用方法

サーバー起動後、`http://localhost:8080` で API にアクセスできます。

### API ドキュメント

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### 使用例

```bash
# ヘルスチェック
curl http://localhost:8080/

# ラベル検出
curl http://localhost:8080/quickstart

# OCR
curl http://localhost:8080/ocr

# OCR + AI分析
curl http://localhost:8080/ocr-and-classify
```

<!-- ## プロジェクト構造

```
giiku/
├── app/
│   ├── main.py              # メインAPIアプリケーション
│   └── __pycache__/
├── static/                  # 画像ファイル
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
├── docker-compose.yml       # Docker Compose設定
├── Dockerfile              # Docker設定
├── requirements.txt        # Python依存関係
├── vision-key.json         # Google Cloud認証キー
├── .env                    # 環境変数（要作成）
└── README.md              # このファイル
``` -->

## 依存関係

```
google-cloud-vision         # Google Cloud Vision API
uvicorn                    # ASGIサーバー
fastapi                    # WebAPIフレームワーク
python-dotenv              # 環境変数管理
google-generativeai        # Google Gemini AI
```

## 開発

### 新しい画像の追加

1. `static/` フォルダに画像を追加
2. `main.py` の該当エンドポイントで `file_path` を更新

### 新しいエンドポイントの追加

`app/main.py` にルート関数を追加して、必要な処理を実装する。

## 注意事項

- API 使用には Google Cloud と Gemini の API キーが必要
- Vision API と Gemini API の使用料金が発生する可能性があり
- `vision-key.json` ファイルは機密情報のため、バージョン管理に含めない
