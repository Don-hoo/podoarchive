from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class LoginConfig:
    username: str
    email: str
    password: str


@dataclass
class TelegramConfig:
    bot_token: str
    chat_id: str


@dataclass
class AppConfig:
    poll_interval_seconds: int
    download_dir: Path
    accounts: list[str]
    cookies_file: Path | None
    auth_token: str | None
    ct0: str | None
    login: LoginConfig | None
    telegram: TelegramConfig | None


def _parse_accounts(raw_accounts) -> list[str]:
    if isinstance(raw_accounts, str):
        items = raw_accounts.split(",")
    elif isinstance(raw_accounts, list):
        items = raw_accounts
    else:
        items = []

    return [str(a).strip().lstrip("@") for a in items if str(a).strip()]


def load_config_from_env() -> AppConfig:
    accounts = _parse_accounts(os.getenv("ARTIST_ACCOUNTS", ""))
    if not accounts:
        raise ValueError("ARTIST_ACCOUNTS 환경 변수에 작가 핸들을 넣어주세요.")

    auth_token = os.getenv("X_AUTH_TOKEN")
    ct0 = os.getenv("X_CT0")
    if not auth_token or not ct0:
        raise ValueError("X_AUTH_TOKEN 과 X_CT0 환경 변수가 필요합니다.")

    telegram = None
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        telegram = TelegramConfig(bot_token=bot_token, chat_id=chat_id)

    return AppConfig(
        poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "300")),
        download_dir=Path(os.getenv("DOWNLOAD_DIR", "downloads")),
        accounts=accounts,
        cookies_file=None,
        auth_token=auth_token,
        ct0=ct0,
        login=None,
        telegram=telegram,
    )


def load_config_from_yaml(path: Path) -> AppConfig:
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    accounts = _parse_accounts(raw.get("accounts", []))
    if not accounts:
        raise ValueError("config.yaml 의 accounts 에 최소 1개 계정을 넣어주세요.")

    login_raw = raw.get("login")
    login = None
    if login_raw:
        login = LoginConfig(
            username=str(login_raw["username"]),
            email=str(login_raw.get("email", login_raw["username"])),
            password=str(login_raw["password"]),
        )

    telegram = None
    telegram_raw = raw.get("telegram")
    if telegram_raw:
        telegram = TelegramConfig(
            bot_token=str(telegram_raw["bot_token"]),
            chat_id=str(telegram_raw["chat_id"]),
        )

    cookies_file = raw.get("cookies_file")
    return AppConfig(
        poll_interval_seconds=int(raw.get("poll_interval_seconds", 300)),
        download_dir=Path(raw.get("download_dir", "downloads")),
        accounts=accounts,
        cookies_file=Path(cookies_file) if cookies_file else None,
        auth_token=raw.get("auth_token"),
        ct0=raw.get("ct0"),
        login=login,
        telegram=telegram,
    )


def load_config(path: Path = Path("config.yaml")) -> AppConfig:
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("X_AUTH_TOKEN"):
        return load_config_from_env()

    if path.exists():
        return load_config_from_yaml(path)

    raise FileNotFoundError(
        f"설정 파일이 없습니다: {path}\n"
        f"config.example.yaml 을 복사해서 config.yaml 을 만들거나, "
        f"GitHub Secrets / 환경 변수를 설정하세요."
    )
