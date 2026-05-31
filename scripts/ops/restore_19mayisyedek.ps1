# 19mayisyedek geri dönüş — çalışma ağacını yedek anına sıfırlar.
# Kullanım: .\scripts\ops\restore_19mayisyedek.ps1
# Alternatif: "19mayısyedek'e dön" deyip bu betiği çalıştırın.

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not (Test-Path (Join-Path $Root ".git"))) {
    $Root = "C:\kokpitim"
}
Set-Location $Root

$ref = "19mayisyedek"
$commit = "0192ee5"

Write-Host "Kokpitim -> $ref ($commit) geri dönüşü" -ForegroundColor Cyan
Write-Host "UYARI: Kaydedilmemiş tüm değişiklikler silinecek." -ForegroundColor Yellow
$confirm = Read-Host "Devam? (evet/hayir)"
if ($confirm -notmatch "^(evet|e|yes|y)$") {
    Write-Host "İptal." -ForegroundColor Gray
    exit 0
}

git fetch --all 2>$null
git checkout $ref 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout -B $ref $commit
}
git reset --hard $commit
git clean -fd -e .env -e .venv -e instance

Write-Host "Tamam. HEAD: $(git log -1 --oneline)" -ForegroundColor Green
Write-Host "main'e dönmek için: git checkout main" -ForegroundColor Gray
