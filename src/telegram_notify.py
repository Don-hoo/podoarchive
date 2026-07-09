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


async def send_text_post(
    telegram: TelegramConfig,
    username: str,
    tweet_text: str | None,
    tweet_url: str | None = None,
) -> None:
    """이미지/영상이 없는, 텍스트만 있는 게시물을 텔레그램으로 전송합니다."""
    text_parts = [f"@{username}"]
    if tweet_text:
        text_parts.append(tweet_text[:3500])
    if tweet_url:
        text_parts.append(tweet_url)
    message = "\n\n".join(text_parts)

    url = f"https://api.telegram.org/bot{telegram.bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            data={
                "chat_id": telegram.chat_id,
                "text": message,
                "disable_web_page_preview": "false",
            },
        )
        response.raise_for_status()
    logger.info("Telegram 텍스트 전송 완료: @%s", username)
