from app.core.config import settings

MAX_BYTES = settings.max_file_size_mb * 1024 * 1024

def is_mime_allowed(mime: str | None) -> bool:
    if not mime:
        return False
    if mime in settings.disallowed_mime_types:
        return False
    if settings.allowed_mime_types and mime not in settings.allowed_mime_types:
        return False
    return True

async def read_limited(upload_file, max_bytes: int = MAX_BYTES) -> bytes:
    """
    UploadFile からサイズ上限つきで読み込み。
    上限超過なら空の bytes を返し、呼び出し側で 413 を返す。
    """
    # UploadFileはSpooledTemporaryFile。read(size)で分割読み取り可
    chunk = await upload_file.read(max_bytes + 1)  # 上限+1で超過検出
    if len(chunk) > max_bytes:
        return b""
    return chunk
