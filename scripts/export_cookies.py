"""브라우저 쿠키를 cookies.json 형식으로 만들기 위한 도우미.

사용법:
1. Chrome/Edge에서 x.com 로그인
2. F12 → Application → Cookies → https://x.com
3. 아래 이름의 쿠키 Value 를 복사해서 입력 (없는 항목은 Enter 로 건너뛰기)

또는 cookies.json 파일이 이미 있으면 그대로 GitHub Secret X_COOKIES_JSON 에 넣으세요.
"""

from __future__ import annotations

import json
import sys

COOKIE_NAMES = [
    "auth_token",
    "ct0",
    "twid",
    "guest_id",
    "personalization_id",
    "kdt",
]


def main() -> None:
    print("x.com 쿠키 입력 (없으면 Enter):\n")
    cookies: dict[str, str] = {}

    for name in COOKIE_NAMES:
        value = input(f"{name}: ").strip()
        if value:
            cookies[name] = value

    if "auth_token" not in cookies or "ct0" not in cookies:
        print("\n오류: auth_token 과 ct0 는 필수입니다.", file=sys.stderr)
        raise SystemExit(1)

    output_path = "cookies.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)

    print(f"\n저장됨: {output_path}")
    print("\nGitHub Secret 등록:")
    print("  Name: X_COOKIES_JSON")
    print("  Value: 아래 JSON 전체를 한 줄로 복사해서 넣기\n")
    print(json.dumps(cookies, ensure_ascii=False))


if __name__ == "__main__":
    main()
