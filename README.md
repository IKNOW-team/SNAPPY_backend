# 📸 SNAPPY Backend

OCR・画像分析APIサーバー | Google Cloud Vision + Gemini AI

## 📋 概要

SNAPPYは、画像からテキストを抽出し、AIで自動分類するWebAPIサービスです。
Google Cloud VisionとGemini AIを活用し、高精度なOCRと知的な情報分類を実現します。

### ✨ 主な機能

- 🔍 **画像分析**: Google Cloud Visionによる高精度な画像認識
- 📝 **テキスト抽出**: OCRによる多言語テキスト抽出
- 🤖 **AI分類**: Gemini AIによるインテリジェントな情報分類
- 🌐 **REST API**: FastAPIによる高性能なWeb API
- ☁️ **クラウド対応**: Renderでの簡単デプロイ

### 🛠️ 技術スタック

- **バックエンド**: Python 3.10 + FastAPI
- **AI/ML**: Google Cloud Vision API + Gemini AI
- **インフラ**: Docker + Render
- **アーキテクチャ**: モジュラー設計

## 🚀 クイックスタート

### 必要なもの

- Docker Desktop
- Google Cloud アカウント
- Gemini API キー

### 1️⃣ セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/nunupy345345/SNAPPY_backend.git
cd giiku

# 環境変数ファイルを作成
cp .env.example .env

# 環境変数を設定
# - GEMINI_API_KEY
# - GCP_SA_JSON（本番環境用）
# - GOOGLE_APPLICATION_CREDENTIALS（開発環境用）
```

### 2️⃣ 起動

```bash
# Dockerで起動
docker-compose up -d

# 起動確認
curl http://localhost:8080/health
```

## 📚 API仕様

### エンドポイント一覧

| パス | メソッド | 説明 | リクエスト |
|---|---|---|---|
| `/health` | GET | ヘルスチェック | - |
| `/vision/labels` | POST | 画像ラベル検出 | `multipart/form-data` |
| `/ocr/extract` | POST | テキスト抽出 | `multipart/form-data` |
| `/ocr/classify` | POST | テキスト抽出+分類 | `multipart/form-data` |

### AI分類機能

`/ocr/classify` エンドポイントは以下のカテゴリで分類：

1. **ジャンル**: ご飯屋 / 観光地 / 本 / 乗り換え案内 / その他
2. **タイトル**: 店名・本の名前・施設名など
3. **場所**: 住所・市区町村・駅名・位置情報など
4. **備考**: 価格・営業時間・感想など

### 使用例

```bash
# OCR + 分類の実行
curl -X POST http://localhost:8080/ocr/classify \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

### レスポンス例

```json
{
  "ocr_text": "カフェ・ド・パリ\n東京都渋谷区",
  "classification": {
    "genre": "ご飯屋",
    "title": "カフェ・ド・パリ",
    "location": "東京都渋谷区",
    "notes": "営業時間 9:00-22:00"
  }
}

## 📁 プロジェクト構造

```
giiku/
├── app/                    # アプリケーションコード
│   ├── clients/           # APIクライアント
│   │   ├── gemini_client.py  # Gemini AI
│   │   └── vision_client.py  # Vision API
│   ├── core/              # 核となる機能
│   │   ├── config.py      # 設定管理
│   │   ├── lifecycle.py   # アプリケーションライフサイクル
│   │   └── logging.py     # ログ設定
│   ├── routers/           # APIルート
│   │   ├── health.py      # ヘルスチェック
│   │   ├── vision.py      # Vision API
│   │   └── ocr.py         # OCR処理
│   ├── schemas/           # データモデル
│   │   ├── classify.py    # 分類モデル
│   │   ├── common.py      # 共通モデル
│   │   └── ocr.py         # OCRモデル
│   ├── services/          # ビジネスロジック
│   │   ├── batch_handler.py   # バッチ処理
│   │   ├── classify_service.py # 分類
│   │   └── ocr_service.py     # OCR
│   └── utils/             # ユーティリティ
│       ├── file_loader.py # ファイル処理
│       └── validators.py   # バリデーション
├── static/                # 画像ファイル
└── secrets/               # 認証情報

### 開発環境セットアップ

1. Python環境の準備
```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

2. 認証情報の設定
```bash
# Google Cloudの認証情報
mv path/to/your-key.json vision-key.json

# 環境変数の設定
cp .env.example .env
# .envファイルを編集
```

3. 開発サーバーの起動
```bash
# FastAPI開発サーバー
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

## 💻 開発ガイド

### 新機能の追加手順

1. **スキーマの定義**
```python
# app/schemas/new_feature.py
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    param: str

class NewFeatureResponse(BaseModel):
    result: str
```

2. **サービスの実装**
```python
# app/services/new_feature_service.py
class NewFeatureService:
    async def process(self, data: str) -> str:
        # ビジネスロジックの実装
        return result
```

3. **ルーターの追加**
```python
# app/routers/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.post("/new-feature")
async def new_feature(request: NewFeatureRequest):
    result = await service.process(request.param)
    return NewFeatureResponse(result=result)
```

4. **メインアプリへの登録**
```python
# app/main.py
from app.routers import new_feature
app.include_router(new_feature.router)
```

### テスト方法

```bash
# 単体テスト
pytest tests/unit

# 統合テスト
pytest tests/integration

# カバレッジレポート
coverage run -m pytest
coverage report
```

### API ドキュメント

開発中は以下のURLでAPIドキュメントを確認できます：

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## 🚀 デプロイメント

### Render へのデプロイ

1. **Renderでの設定**
   - リポジトリを連携
   - ビルド設定は自動検出（Dockerfile使用）

2. **環境変数の設定**
```env
GEMINI_API_KEY=your_key_here
GCP_SA_JSON={"type":"service_account",...}
```

3. **デプロイ開始**
   - `main` ブランチへのプッシュで自動デプロイ
   - または手動でデプロイを実行

### Docker本番環境

```bash
# イメージビルド
docker build -t snappy-backend .

# コンテナ起動
docker run -d \
  --name snappy-backend \
  -p 8080:8080 \
  -e GEMINI_API_KEY="your_key" \
  -e GCP_SA_JSON='{"type":"service_account",...}' \
  snappy-backend
```

## ⚙️ 設定項目

### 環境変数

| 変数名 | 必須 | 説明 |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Gemini AIのAPIキー |
| `GCP_SA_JSON` | ✅ | Google Cloud認証情報 |
| `PORT` | - | サーバーポート (default: 8080) |

### API制限

- Vision API: 1000リクエスト/分
- Gemini AI: 60リクエスト/分
- 最大画像サイズ: 20MB

## 🔧 トラブルシューティング

### よくある問題

#### 1. 認証エラー
```
google.auth.exceptions.DefaultCredentialsError
```
✅ 認証情報を確認
- ローカル: `vision-key.json` の配置
- 本番: `GCP_SA_JSON` の設定

#### 2. API制限エラー
```
google.api_core.exceptions.ResourceExhausted
```
✅ 使用量を確認
- Vision APIの利用制限
- Gemini APIの利用制限

### ログの確認

```bash
# Dockerログ
docker-compose logs -f app

# アプリケーションログ
tail -f logs/app.log
```

## 📝 その他

### セキュリティ

- 🔑 APIキーは必ず環境変数で管理
- 🔒 認証情報はGitで管理しない
- 🛡️ 本番環境ではCORSを制限

### パフォーマンス

- 📦 画像は最適化してアップロード
- 🚀 バッチ処理は非同期で実行
- 💾 結果をキャッシュ

## 🤝 コントリビューション

1. Forkする
2. フィーチャーブランチを作成
3. 変更をコミット
4. プルリクエストを作成

## 📝 ライセンス

MIT License

## 👥 コントリビューション

1. このリポジトリをFork
2. 機能ブランチを作成
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. 変更をコミット
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. プッシュ
   ```bash
   git push origin feature/amazing-feature
   ```
5. プルリクエストを作成

## 📞 サポート

- GitHub Issues: [Report a bug](https://github.com/nunupy345345/SNAPPY_backend/issues)
- Email: [your-email@example.com](mailto:your-email@example.com)

## 📄 ライセンス

このプロジェクトはMIT Licenseの下で公開されています。

## 👨‍💻 開発者

- **メインメンテナ**: [@nunupy345345](https://github.com/nunupy345345)

---

Made with ❤️ by SNAPPY Team

### メイン依存関係

| パッケージ            | バージョン | 用途                                 |
| --------------------- | ---------- | ------------------------------------ |
| `google-cloud-vision` | latest     | Google Cloud Vision API クライアント |
| `google-generativeai` | latest     | Google Gemini AI クライアント        |
| `fastapi`             | latest     | WebAPI フレームワーク                |
| `uvicorn`             | latest     | ASGI サーバー                        |
| `python-dotenv`       | latest     | 環境変数管理                         |

### 完全な requirements.txt

```
google-cloud-vision         # Google Cloud Vision API
uvicorn                    # ASGIサーバー
fastapi                    # WebAPIフレームワーク
python-dotenv              # 環境変数管理
google-generativeai        # Google Gemini AI
```

## 開発

### 開発環境のセットアップ

```bash
# 開発用の仮想環境作成
python -m venv venv
source venv/bin/activate

# 開発用依存関係のインストール（今後追加予定）
pip install -r requirements.txt
# pip install -r requirements-dev.txt  # 将来的にテスト用パッケージなど
```

### コード構成のガイドライン

#### 新しい画像の追加

1. `static/` フォルダに画像を追加
2. `app/main.py` の該当エンドポイントで `file_path` を更新

#### 新しいエンドポイントの追加

1. `app/main.py` にルート関数を追加
2. 必要に応じてサービス層を分離（推奨構造参照）

#### 推奨されるコード分離

現在は `main.py` に全てが含まれていますが、将来的には以下のような分離が推奨されます：

```python
# app/services/vision_service.py
class VisionService:
    def detect_labels(self, image_path: str):
        # ラベル検出ロジック
        pass

    def extract_text(self, image_path: str):
        # OCRロジック
        pass

# app/services/gemini_service.py
class GeminiService:
    def classify_text(self, text: str):
        # テキスト分類ロジック
        pass
```

### テストの実行

```bash
# 将来的なテスト実行コマンド
# pytest tests/
# coverage run -m pytest tests/
```

## デプロイメント

### Docker を使った本番デプロイ

```bash
# 本番用ビルド
docker build -t snappy-backend .

# 本番実行
docker run -d \
  --name snappy-backend \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/vision-key.json:/app/vision-key.json \
  -v $(pwd)/static:/app/static \
  snappy-backend
```

### 環境設定のチェックリスト

- [ ] `.env` ファイルが作成されている
- [ ] `GEMINI_API_KEY` が設定されている
- [ ] `vision-key.json` ファイルが配置されている
- [ ] Google Cloud Vision API が有効化されている
- [ ] テスト画像が `static/` フォルダに配置されている

## トラブルシューティング

### よくある問題と解決方法

#### 1. Google Cloud 認証エラー

```
google.auth.exceptions.DefaultCredentialsError
```

**解決方法**:

- `vision-key.json` ファイルがプロジェクトルートに配置されているか確認
- `GOOGLE_APPLICATION_CREDENTIALS` 環境変数が正しく設定されているか確認

#### 2. Gemini API エラー

```
google.generativeai.types.GenerationException
```

**解決方法**:

- `GEMINI_API_KEY` が正しく設定されているか確認
- API キーに適切な権限があるか確認

#### 3. 画像ファイルが見つからない

```
FileNotFoundError: [Errno 2] No such file or directory
```

**解決方法**:

- `static/` フォルダに対象の画像ファイルが存在するか確認
- ファイルパスが正しいか確認

### ログの確認

```bash
# Docker実行時のログ確認
docker-compose logs -f

# 特定のサービスのログ確認
docker-compose logs -f app
```

## 注意事項

- API 使用には Google Cloud と Gemini の API キーが必要
- Vision API と Gemini API の使用料金が発生する可能性があり
- `vision-key.json` ファイルは機密情報のため、バージョン管理に含めない
