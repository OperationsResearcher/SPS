# Hizli GCP yedek: kod MINIMAL (~30-80 MB), Yedekler/.git HARIC
# Kullanim: .\scripts\ops\gcp_pull_minimal.ps1
$ErrorActionPreference = 'Stop'
$Host.UI.RawUI.WindowTitle = 'Kokpitim GCP Minimal Kod Yedegi'

$KeyPath = "$env:TEMP\kokpitim_vm_temp_key"
$Ip = '35.246.135.36'
$Base = 'C:\kokpitim\backups\oracle_migration'
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$Remote = "/tmp/kokpitim_code_minimal_${ts}.tar.gz"
$Local = Join-Path $Base "kokpitim_code_minimal_${ts}.tar.gz"

function Write-Log([string]$msg) {
    $line = ('[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'), $msg)
    Write-Host $line
}

Clear-Host
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  GCP MINIMAL Kod Yedegi (hizli)' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'Haric: Yedekler (470MB), .git (747MB), backups, instance, *.db kok' -ForegroundColor Yellow
Write-Host ''

# Eski yavas indirmeyi durdur
Get-Process scp -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Log 'VM uzerinde kucuk arsiv olusturuluyor...'
$tarCmd = @(
    "sudo tar czf $Remote -C /home/kokpitim.com/public_html",
    '--exclude=Yedekler',
    '--exclude=backups',
    '--exclude=instance',
    '--exclude=.git',
    '--exclude=__pycache__',
    '--exclude=.venv',
    '--exclude=node_modules',
    '--exclude=*.db',
    '--exclude=.tmp.driveupload',
    '.',
    "&& sudo chmod a+r $Remote && ls -lah $Remote"
) -join ' '
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=120 -i $KeyPath "mfgulen4660@${Ip}" $tarCmd

$remoteSize = ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i $KeyPath "mfgulen4660@${Ip}" "stat -c%s $Remote"
$TargetBytes = [long]$remoteSize
Write-Log "VM arsiv boyutu: $([math]::Round($TargetBytes/1MB,2)) MB"

Write-Log 'Indirme basliyor...'
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = 'scp'
$psi.Arguments = "-o StrictHostKeyChecking=no -o ServerAliveInterval=15 -i `"$KeyPath`" mfgulen4660@${Ip}:${Remote} `"$Local`""
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$proc = [System.Diagnostics.Process]::Start($psi)

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$lastBytes = 0L
$lastTime = $sw.Elapsed.TotalSeconds
while (-not $proc.HasExited) {
    $bytes = if (Test-Path $Local) { (Get-Item $Local).Length } else { 0 }
    $pct = [math]::Min(99, [math]::Round(100.0 * $bytes / $TargetBytes, 1))
    $mbDone = [math]::Round($bytes / 1MB, 2)
    $mbTotal = [math]::Round($TargetBytes / 1MB, 2)
    $mbLeft = [math]::Max(0, [math]::Round(($TargetBytes - $bytes) / 1MB, 2))
    $dt = $sw.Elapsed.TotalSeconds - $lastTime
    if ($dt -ge 1 -and $bytes -gt $lastBytes) {
        $speed = ($bytes - $lastBytes) / 1MB / $dt
        $lastBytes = $bytes
        $lastTime = $sw.Elapsed.TotalSeconds
        $eta = if ($speed -gt 0.01) { [math]::Round($mbLeft / $speed / 60, 1) } else { '?' }
    } else { $speed = 0; $eta = '?' }
    Write-Progress -Activity 'Minimal kod yedegi' -Status "Indirildi: $mbDone / $mbTotal MB | Kalan: $mbLeft MB | $([math]::Round($speed,2)) MB/s | ETA: $eta dk" -PercentComplete $pct
    Start-Sleep -Milliseconds 500
}
Write-Progress -Activity 'Minimal kod yedegi' -Completed
$proc.WaitForExit()
if ($proc.ExitCode -ne 0) { throw "SCP exit $($proc.ExitCode)" }

ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -i $KeyPath "mfgulen4660@${Ip}" "sudo rm -f $Remote" | Out-Null
$final = (Get-Item $Local).Length
Write-Host "TAMAM: $([math]::Round($final/1MB,2)) MB -> $Local" -ForegroundColor Green
Write-Host "Not: Tam uygulama kodu zaten C:\kokpitim (git) ve Oracle'a git pull ile gidecek." -ForegroundColor Cyan
Read-Host 'Enter ile kapat'
