from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from twikit import Client

from config import AppConfig
from storage import ArchiveStore
from telegram_notify import send_archived_media

logger = logging.getLogger(__name__)


class XArtArchiver:
    def __init__(self, config: AppConfig, store: ArchiveStore) -> None:
        self.config = config
        self.store = store
        self.client = Client("ko-KR")

    async def authenticate(self) -> None:
        if self.config.cookies_file and self.config.cookies_file.exists():
            self.client.load_cookies(str(self.config.cookies_file))
            logger.info("쿠키 파일 로드: %s", self.config.cookies_file)
            return

        if self.config.auth_token and self.config.ct0:
            self.client.set_cookies(
                {
                    "auth_token": self.config.auth_token,
                    "ct0": self.config.ct0,
                }
            )
            logger.info("config.yaml 의 auth_token / ct0 로 인증")
            return

        if not self.config.login:
            raise RuntimeError(
                "인증 정보가 없습니다. cookies.json, auth_token/ct0, "
                "또는 login 설정 중 하나를 config.yaml 에 추가하세요."
            )

        login = self.config.login
        cookies_path = str(self.config.cookies_file or "cookies.json")
        await self.client.login(
            auth_info_1=login.username,
            auth_info_2=login.email,
            password=login.password,
            cookies_file=cookies_path,
        )
        self.client.save_cookies(cookies_path)
        logger.info("로그인 완료, 쿠키 저장: %s", cookies_path)

    async def archive_account(self, username: str) -> int:
        user = await self.client.get_user_by_screen_name(username)
        result = await self.client.get_user_tweets(user.id, "Tweets", count=40)
        saved = 0

        for tweet in result:
            if not tweet.media:
                continue

            created = tweet.created_at
            if isinstance(created, datetime):
                date_prefix = created.strftime("%Y%m%d_%H%M%S")
            else:
                date_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")

            out_dir = self.config.download_dir / username
            out_dir.mkdir(parents=True, exist_ok=True)

            for index, media in enumerate(tweet.media):
                if self.store.is_archived(tweet.id, index):
                    continue

                ext = self._extension_for_media(media)
                filename = f"{date_prefix}_{tweet.id}_{index}{ext}"
                target = out_dir / filename

                try:
                    await self._download_media(media, target)
                except Exception:
                    logger.exception(
                        "다운로드 실패 @%s tweet=%s media=%s",
                        username,
                        tweet.id,
                        index,
                    )
                    continue

                self.store.mark_archived(
                    tweet_id=tweet.id,
                    media_index=index,
                    username=username,
                    file_path=target,
                    tweet_text=tweet.text,
                )
                saved += 1
                logger.info("저장: %s", target)

                if self.config.telegram:
                    try:
                        await send_archived_media(
                            self.config.telegram,
                            target,
                            username,
                            tweet.text,
                        )
                    except Exception:
                        logger.exception("Telegram 전송 실패: %s", target)

        return saved

    @staticmethod
    def _extension_for_media(media) -> str:
        media_type = getattr(media, "type", "")
        if media_type == "photo":
            return ".jpg"
        if media_type in {"video", "animated_gif"}:
            return ".mp4"
        return ".bin"

    @staticmethod
    async def _download_media(media, target: Path) -> None:
        media_type = getattr(media, "type", "")
        if media_type == "photo":
            await media.download(str(target))
            return

        if media_type in {"video", "animated_gif"}:
            await media.streams[-1].download(str(target))
            return

        raise ValueError(f"지원하지 않는 미디어 타입: {media_type}")

    async def run_once(self) -> int:
        total = 0
        for username in self.config.accounts:
            try:
                saved = await self.archive_account(username)
                total += saved
                logger.info("@%s: 새로 저장한 미디어 %d개", username, saved)
            except Exception:
                logger.exception("@%s 처리 중 오류", username)
        return total

    async def run_forever(self) -> None:
        await self.authenticate()
        logger.info(
            "모니터링 시작: %s (주기 %ds)",
            ", ".join(f"@{a}" for a in self.config.accounts),
            self.config.poll_interval_seconds,
        )

        while True:
            saved = await self.run_once()
            if saved:
                logger.info("이번 주기 저장 합계: %d개", saved)
            await asyncio.sleep(self.config.poll_interval_seconds)
