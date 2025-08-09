# app/services/batch_handler.py
from fastapi import UploadFile
from pydantic import ValidationError
from typing import List
import json

from app.schemas.classify import TaggedItem
from app.utils.validators import is_mime_allowed, read_limited
from app.utils.threads import run_sync
from app.core.config import settings
from app.services.ocr_service import OCRService
from app.services.classify_service import ClassifyService

async def handle_one_file(
    f: UploadFile,
    ocr: OCRService,
    classifier: ClassifyService,
    candidate_tags: List[List[str]],
) -> TaggedItem:
    name = f.filename or "unnamed"

    if not is_mime_allowed(f.content_type):
        return TaggedItem(**{
            "status.success": False,
            "tag": candidate_tags[0][0] if candidate_tags else "location",
            "title": name,
            "location": "",
            "description": f"Unsupported Media Type: {f.content_type}",
        })

    data = await read_limited(f)
    if not data:
        return TaggedItem(**{
            "status.success": False,
            "tag": candidate_tags[0][0] if candidate_tags else "location",
            "title": name,
            "location": "",
            "description": f"File too large (> {settings.max_file_size_mb}MB) or empty",
        })

    try:
        text = await run_sync(ocr.run_ocr_bytes, data)
        payload = await run_sync(classifier.classify_json_with_tags, text, candidate_tags)

        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list) or not results:
            raise ValueError("results missing")

        item = TaggedItem.model_validate(results[0])
        return item

    except (ValidationError, ValueError, TypeError) as e:
        return TaggedItem(**{
            "status.success": False,
            "tag": candidate_tags[0][0] if candidate_tags else "location",
            "title": (text or name)[:30] if 'text' in locals() else name,
            "location": "",
            "description": f"Invalid LLM output: {str(e)}",
        })
    except Exception as e:
        return TaggedItem(**{
            "status.success": False,
            "tag": candidate_tags[0][0] if candidate_tags else "location",
            "title": name,
            "location": "",
            "description": f"Processing error: {str(e)}",
        })
