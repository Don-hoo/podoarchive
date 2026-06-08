# PC 꺼도 되는 무료 클라우드 설정 (약 10분)

GitHub Actions(무료) + Telegram(무료) 조합입니다.
**공개(public) 저장소**면 GitHub Actions 시간 제한이 사실상 없습니다.

---

## 1. Telegram 봇 만들기 (이미지 저장소)

1. Telegram에서 **@BotFather** 검색 → `/newbot` → 이름/아이디 설정
2. 받은 **봇 토큰** 복사 (예: `7123456789:AAH...`)
3. **비공개 채널** 하나 만듦 (예: `my-x-archive`)
4. 채널 설정 → 관리자 → 방금 만든 **봇을 관리자로 추가**
5. 채널에 아무 글 하나 올림
6. 브라우저에서 아래 주소 접속 (TOKEN 자리에 봇 토큰):

   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```

7. `"chat":{"id":-1001234567890` 같은 **chat id** 복사

> 채널 대신 본인과 봇의 **1:1 채팅**도 가능합니다. 봇에게 `/start` 보낸 뒤 getUpdates로 id 확인.

---

## 2. X 쿠키 복사

1. Chrome/Edge에서 [x.com](https://x.com) 로그인
2. `F12` → **Application** → **Cookies** → `https://x.com`
3. 복사:
   - `auth_token`
   - `ct0`

쿠키는 몇 주~몇 달마다 다시 넣어야 할 수 있습니다.

---

## 3. GitHub 저장소 만들기 & 코드 올리기

PowerShell:

```powershell
cd C:\Users\01089\Projects\x-art-archiver

# GitHub CLI 없으면: https://cli.github.com 설치
gh auth login

# 공개 저장소 생성 + 푸시 (이름은 원하면 변경)
gh repo create x-art-archiver --public --source=. --remote=origin --push
```

`gh` 없이 수동으로:

1. GitHub에서 **New repository** → 이름 `x-art-archiver` → **Public**
2. 아래 실행:

```powershell
git remote add origin https://github.com/<본인아이디>/x-art-archiver.git
git add .
git commit -m "Add cloud archiver with GitHub Actions"
git branch -M main
git push -u origin main
```

---

## 4. GitHub Secrets 등록

저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 이름 | 값 |
|-------------|-----|
| `X_AUTH_TOKEN` | x.com 쿠키 auth_token |
| `X_CT0` | x.com 쿠키 ct0 |
| `ARTIST_ACCOUNTS` | 작가 핸들 (@ 없이). 여러 명: `artist1,artist2` |
| `TELEGRAM_BOT_TOKEN` | BotFather 토큰 |
| `TELEGRAM_CHAT_ID` | Telegram chat id (예: `-1001234567890`) |

PowerShell로 한 번에 (값은 본인 것으로 바꾸기):

```powershell
gh secret set X_AUTH_TOKEN --body "여기에_auth_token"
gh secret set X_CT0 --body "여기에_ct0"
gh secret set ARTIST_ACCOUNTS --body "artist_handle"
gh secret set TELEGRAM_BOT_TOKEN --body "봇토큰"
gh secret set TELEGRAM_CHAT_ID --body "-1001234567890"
```

---

## 5. 동작 확인

1. GitHub 저장소 → **Actions** 탭
2. **Archive X Media** → **Run workflow** (수동 1회 테스트)
3. 성공하면 5분마다 자동 실행
4. Telegram 채널에 그림이 오는지 확인

---

## 어떻게 돌아가나요?

```
[GitHub Actions — 5분마다]
       ↓
  X 타임라인 확인
       ↓
  새 그림 발견 → Telegram 채널로 전송
       ↓
  archive.db 를 data 브랜치에 저장 (중복 방지)
```

- **PC는 꺼도 됩니다** — GitHub 서버에서 실행
- **비용 0원** — public repo Actions + Telegram
- 저장된 그림은 **Telegram 앱**에서 언제든 확인

---

## 자주 묻는 것

**Q. 5분보다 더 자주 확인할 수 있나요?**  
A. GitHub Actions cron 최소 간격이 5분입니다. 더 촘촘히 하려면 Oracle Cloud 무료 VPS 등이 필요합니다.

**Q. 쿠키 만료되면?**  
A. Actions가 실패합니다. GitHub Secrets에서 `X_AUTH_TOKEN`, `X_CT0` 를 새 값으로 업데이트하세요.

**Q. Telegram 말고 다른 저장소?**  
A. Google Drive(rclone), NAS 등으로 확장 가능합니다. 필요하면 요청하세요.

**Q. 비공개 저장소는?**  
A. 가능하지만 Actions 무료 한도(월 2000분)가 있어 5분 주기에는 부족할 수 있습니다. **Public 권장.**
