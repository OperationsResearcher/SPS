# VM yedek indirme ilerlemesi — canlı izleme
# Kullanım: .\scripts\ops\oracle\izle_vm_indirme.ps1

param(
    [string]$File = 'C:\kokpitim\backups\vm_pull\full_20260524_104728\app_code.tar.gz',
    [double]$HedefMB = 483,
    [int]$AralikSaniye = 2
)

if (-not (Test-Path $File)) {
    Write-Host "Dosya henuz yok: $File" -ForegroundColor Yellow
    Write-Host "Indirme baslayinca bu betik ilerlemeyi gosterir."
}

while ($true) {
    Clear-Host
    $now = Get-Date -Format 'HH:mm:ss'
    Write-Host "=== VM yedek indirme — $now ===" -ForegroundColor Cyan
    Write-Host "Dosya: $File"
    Write-Host ""

    if (Test-Path $File) {
        $info = Get-Item $File
        $mb = $info.Length / 1MB
        $pct = if ($HedefMB -gt 0) { [math]::Min(100, ($mb / $HedefMB) * 100) } else { 0 }
        $barLen = 40
        $filled = [int][math]::Floor($barLen * $pct / 100)
        $bar = ('#' * $filled) + ('-' * ($barLen - $filled))

        Write-Host ("  {0:N1} MB / {1:N0} MB  ({2:N1}%)" -f $mb, $HedefMB, $pct)
        Write-Host "  [$bar]"
        Write-Host ("  Son degisim: {0}" -f $info.LastWriteTime.ToString('HH:mm:ss'))
    } else {
        Write-Host "  Bekleniyor..." -ForegroundColor Yellow
        $mb = 0
        $pct = 0
    }

    $scp = @(Get-Process scp -ErrorAction SilentlyContinue)
    Write-Host ""
    if ($scp.Count -gt 0) {
        Write-Host "  scp: CALISIYOR ($($scp.Count) surec)" -ForegroundColor Green
    } else {
        Write-Host "  scp: DURDU" -ForegroundColor $(if ($pct -ge 99) { 'Green' } else { 'Red' })
    }

    Write-Host ""
    Write-Host "Cikis: Ctrl+C  |  Yenileme: her ${AralikSaniye}s" -ForegroundColor DarkGray

    if ($scp.Count -eq 0 -and (Test-Path $File) -and $mb -ge ($HedefMB * 0.98)) {
        Write-Host ""
        Write-Host "Indirme tamamlandi." -ForegroundColor Green
        break
    }
    if ($scp.Count -eq 0 -and (Test-Path $File) -and $mb -lt ($HedefMB * 0.9)) {
        Write-Host ""
        Write-Host "scp durdu ama dosya eksik — yeniden baslatin:" -ForegroundColor Red
        Write-Host "  .\scripts\ops\oracle\vm_pull_to_local.ps1 -SkipVmBackup"
        break
    }

    Start-Sleep -Seconds $AralikSaniye
}
