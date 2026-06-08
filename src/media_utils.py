from __future__ import annotations

import re


def original_photo_url(url: str) -> str:
    """X 이미지 URL을 원본(name=orig)으로 변환."""
    if not url:
        return url

    if "pbs.twimg.com" not in url:
        return url

    if "name=" in url:
        return re.sub(r"name=[^&]+", "name=orig", url)

    separator = "&" if "?" in url else "?"
    return f"{url}{separator}name=orig"
