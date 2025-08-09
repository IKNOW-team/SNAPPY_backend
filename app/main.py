from fastapi import FastAPI
from app.core.lifecycle import lifespan
from app.routers import health, vision, ocr
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan, title="Vision & Gemini API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は限定推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルータ登録
app.include_router(health.router)
app.include_router(vision.router)
app.include_router(ocr.router)