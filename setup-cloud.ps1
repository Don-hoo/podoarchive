#Requires -Version 5.1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== x-art-archiver 클라우드 설정 도우미 ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI(gh)가 없습니다." -ForegroundColor Yellow
    Write-Host "설치: https://cli.github.com" -ForegroundColor Yellow
    Write-Host "또는 SETUP_CLOUD.md 의 수동 단계를 따라주세요."
    exit 1
}

$loggedIn = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "GitHub 로그인이 필요합니다: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "1) SETUP_CLOUD.md 를 열어 Telegram 봇 + X 쿠키를 준비하세요."
Write-Host "2) 아래 Secrets 값을 입력합니다 (입력 내용은 GitHub에만 저장됩니다)."
Write-Host ""

$authToken = Read-Host "X auth_token"
$ct0 = Read-Host "X ct0"
$accounts = Read-Host "작가 핸들 (@ 없이, 여러 명은 쉼표 구분)"
$tgToken = Read-Host "Telegram bot token"
$tgChat = Read-Host "Telegram chat id"

if (-not (Test-Path ".git")) {
    git init | Out-Null
}

$hasRemote = git remote get-url origin 2>$null
if (-not $hasRemote) {
    $repoName = Read-Host "GitHub 저장소 이름 [x-art-archiver]"
    if (-not $repoName) { $repoName = "x-art-archiver" }

    Write-Host "공개 저장소 생성 및 푸시 중..." -ForegroundColor Green
    git add .
    git commit -m "Add x-art-archiver with GitHub Actions" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "커밋할 변경 없음 또는 이미 커밋됨" -ForegroundColor DarkGray
    }
    gh repo create $repoName --public --source=. --remote=origin --push
} else {
    Write-Host "origin remote 존재: $hasRemote" -ForegroundColor DarkGray
    git add .
    git commit -m "Update x-art-archiver" 2>$null
    git push origin main 2>$null
    if ($LASTEXITCODE -ne 0) { git push origin master 2>$null }
}

Write-Host "GitHub Secrets 등록 중..." -ForegroundColor Green
gh secret set X_AUTH_TOKEN --body $authToken
gh secret set X_CT0 --body $ct0
gh secret set ARTIST_ACCOUNTS --body $accounts
gh secret set TELEGRAM_BOT_TOKEN --body $tgToken
gh secret set TELEGRAM_CHAT_ID --body $tgChat

Write-Host ""
Write-Host "완료!" -ForegroundColor Green
Write-Host "GitHub → Actions → Archive X Media → Run workflow 로 테스트하세요."
Write-Host "자세한 설명: SETUP_CLOUD.md"
Write-Host ""
