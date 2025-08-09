from contextlib import asynccontextmanager
import os
from .config import settings
from .logging import setup_logging

@asynccontextmanager
async def lifespan(app):
    # 事前設定
    setup_logging(settings.debug)

    # Google 認証キーを環境変数へ（Vision SDK は自動検出）
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials

    yield

    # 終了処理（今は特になし）