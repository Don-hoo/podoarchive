from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from archiver import XArtArchiver
from config import load_config
from storage import ArchiveStore


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="X(트위터) 계정의 그림/미디어를 주기적으로 자동 저장합니다."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="설정 파일 경로 (기본: config.yaml)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="1회만 실행하고 종료 (테스트용)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="자세한 로그 출력",
    )
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    setup_logging(args.verbose)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        logging.error("%s", exc)
        return 1

    store = ArchiveStore(Path("archive.db"))
    archiver = XArtArchiver(config, store)

    try:
        await archiver.authenticate()
    except Exception as exc:
        logging.error("인증 실패: %s", exc)
        return 1

    if args.once:
        saved = await archiver.run_once()
        logging.info("완료. 새로 저장: %d개", saved)
        return 0

    await archiver.run_forever()
    return 0


def main() -> None:
    try:
        raise SystemExit(asyncio.run(async_main()))
    except KeyboardInterrupt:
        print("\n종료합니다.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
