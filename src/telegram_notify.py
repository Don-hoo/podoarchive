from __future__ import annotations

import logging
from pathlib import Path

import httpx

from config import TelegramConfig

logger = logging.getLogger(__name__)

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".gif", ".mov"}


async def send_archived_media(
    telegram: TelegramConfig,
    file_path: Path,
    username: str,
    tweet_text: str | None,
) -> None:
    suffix = file_path.suffix.lower()

    # sendPhoto는 Telegram이 압축함 → 원본은 sendDocument 사용
    if suffix in PHOTO_EXTENSIONS:
        method = "sendDocument"
        field = "document"
    elif suffix in VIDEO_EXTENSIONS:
        method = "sendVideo"
        field = "video"
    else:
        method = "sendDocument"
        field = "document"

    caption_parts = [f"@{username}", file_path.name]
    if tweet_text:
        caption_parts.append(tweet_text[:900])
    caption = "\n".join(caption_parts)

    url = f"https://api.telegram.org/bot{telegram.bot_token}/{method}"
    async with httpx.AsyncClient(timeout=120) as client:
        with file_path.open("rb") as handle:
            response = await client.post(
                url,
                data={"chat_id": telegram.chat_id, "caption": caption},
                files={field: (file_path.name, handle)},
            )
        response.raise_for_status()

    logger.info("Telegram 전송 완료 (원본): %s", file_path.name)
