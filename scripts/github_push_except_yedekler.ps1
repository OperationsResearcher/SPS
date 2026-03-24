param(
    [Parameter(Mandatory = $true)]
    [string]$Message,
    [string]$Branch = "main",
    [string]$Remote = "origin"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Git durum kontrolu" -ForegroundColor Cyan
git rev-parse --is-inside-work-tree | Out-Null

Write-Host "==> Tum degisiklikler sahneye aliniyor" -ForegroundColor Cyan
git add -A

# Yedekler klasorunu her kosulda commit disi birak
Write-Host "==> Yedekler klasoru commit disi birakiliyor" -ForegroundColor Cyan
git reset -- "Yedekler/"

Write-Host "==> Sahnedeki degisiklikler" -ForegroundColor Cyan
git diff --cached --name-only

$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Host "Commitlenecek degisiklik kalmadi. (Yedekler haric)" -ForegroundColor Yellow
    exit 0
}

Write-Host "==> Commit olusturuluyor" -ForegroundColor Cyan
git commit -m $Message

Write-Host "==> Push: $Remote/$Branch" -ForegroundColor Cyan
git push $Remote $Branch

Write-Host "Tamamlandi." -ForegroundColor Green
