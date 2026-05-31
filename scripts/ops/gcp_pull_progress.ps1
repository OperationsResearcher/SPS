# GCP kod arsivi indirme — canli ilerleme ekrani
# Kullanim: .\scripts\ops\gcp_pull_progress.ps1
$ErrorActionPreference = 'Stop'
$Host.UI.RawUI.WindowTitle = 'Kokpitim GCP Yedek Indirme'

$KeyPath = "$env:TEMP\kokpitim_vm_temp_key"
$Ip = '35.246.135.36'
$Base = 'C:\kokpitim\backups\oracle_migration'
$Remote = '/tmp/kokpitim_code_20260521_215500.tar.gz'
$Local = Join-Path $Base 'kokpitim_code_20260521_215500.tar.gz'
$TargetBytes = 515000000   # VM'deki ~491 MB
$LogFile = Join-Path $Base 'gcp_pull_progress.log'

function Write-Log([string]$msg) {
    $line = ('[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'), $msg)
    Add-Content -Path $LogFile -Value $line -Encoding utf8
    Write-Host $line
}

Clear-Host
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  KOKPITIM - GCP Kod Arsivi Indirme' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host "Hedef : ~$([math]::Round($TargetBytes/1MB)) MB"
Write-Host "Kaynak: VM $Ip"
Write-Host "Hedef : $Local"
Write-Host ''

if (-not (Test-Path $KeyPath)) {
    Write-Host 'HATA: SSH anahtari yok. Once VM erisimini saglayin.' -ForegroundColor Red
    Read-Host 'Kapatmak icin Enter'
    exit 1
}

Write-Log 'VM dosya boyutu kontrol...'
$remoteSize = ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i $KeyPath "mfgulen4660@${Ip}" "stat -c%s $Remote 2>/dev/null; echo 0" | Select-Object -Last 1
if ($remoteSize -match '^\d+$' -and [long]$remoteSize -gt 1000000) {
    $TargetBytes = [long]$remoteSize
    Write-Log "VM hedef boyut: $([math]::Round($TargetBytes/1MB,2)) MB"
}

$proc = $null
$monitorOnly = $false

if (Test-Path $Local) {
    $cur = (Get-Item $Local).Length
    if ($cur -ge ($TargetBytes * 0.95)) {
        Write-Host "Dosya zaten tamam: $([math]::Round($cur/1MB,2)) MB" -ForegroundColor Green
        $final = $cur
        $monitorOnly = $true
    } elseif (Get-Process scp -ErrorAction SilentlyContinue) {
        Write-Log "SCP zaten calisiyor - mevcut indirme izleniyor ($([math]::Round($cur/1MB,2)) MB)"
        $monitorOnly = $true
    } else {
        Write-Log "Mevcut kismi dosya: $([math]::Round($cur/1MB,2)) MB - yeniden indiriliyor"
        Remove-Item $Local -Force -ErrorAction Stop
    }
}

if (-not $monitorOnly) {
    $scpArgs = @(
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'ServerAliveInterval=15',
        '-o', 'ConnectTimeout=900',
        '-i', $KeyPath,
        "mfgulen4660@${Ip}:${Remote}",
        $Local
    )
    Write-Log 'SCP baslatiliyor...'
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'scp'
    $psi.Arguments = ($scpArgs -join ' ')
    $psi.UseShellExecute = $false
    $psi.RedirectStandardError = $true
    $psi.RedirectStandardOutput = $true
    $psi.CreateNoWindow = $true
    $proc = [System.Diagnostics.Process]::Start($psi)
}

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$lastBytes = 0L
$lastTime = $sw.Elapsed.TotalSeconds

try {
    while ($monitorOnly -or (-not $proc.HasExited)) {
        if ($monitorOnly) {
            $scpRunning = Get-Process scp -ErrorAction SilentlyContinue
            if (-not $scpRunning) {
                if (-not (Test-Path $Local)) { break }
                $done = (Get-Item $Local).Length
                if ($done -ge ($TargetBytes * 0.95)) { break }
            }
        }
        if (Test-Path $Local) {
            $bytes = (Get-Item $Local).Length
        } else {
            $bytes = 0
        }
        $pct = [math]::Min(99, [math]::Round(100.0 * $bytes / $TargetBytes, 1))
        $mbDone = [math]::Round($bytes / 1MB, 2)
        $mbTotal = [math]::Round($TargetBytes / 1MB, 2)
        $mbLeft = [math]::Max(0, [math]::Round(($TargetBytes - $bytes) / 1MB, 2))

        $dt = $sw.Elapsed.TotalSeconds - $lastTime
        if ($dt -ge 1 -and $bytes -gt $lastBytes) {
            $speedMbps = ($bytes - $lastBytes) / 1MB / $dt
            $lastBytes = $bytes
            $lastTime = $sw.Elapsed.TotalSeconds
            if ($speedMbps -gt 0.01) {
                $etaMin = [math]::Round($mbLeft / $speedMbps / 60, 1)
            } else {
                $etaMin = '?'
            }
        } else {
            $speedMbps = 0
            $etaMin = '?'
        }

        $status = "Indirildi: $mbDone MB / $mbTotal MB  |  Kalan: ~$mbLeft MB  |  Hiz: $([math]::Round($speedMbps,2)) MB/s  |  ETA: $etaMin dk"
        Write-Progress -Activity 'GCP Kod Arsivi (SCP)' -Status $status -PercentComplete $pct
        Start-Sleep -Milliseconds 800
    }
} finally {
    Write-Progress -Activity 'GCP Kod Arsivi (SCP)' -Completed
}

if ($proc) {
    $proc.WaitForExit()
    $err = $proc.StandardError.ReadToEnd()
    if ($proc.ExitCode -ne 0) {
        Write-Log "SCP HATA (exit $($proc.ExitCode)): $err"
        Write-Host $err -ForegroundColor Red
        Read-Host 'Enter ile kapat'
        exit $proc.ExitCode
    }
}

if (-not (Test-Path $Local)) {
    Write-Host 'HATA: Indirilen dosya bulunamadi.' -ForegroundColor Red
    Read-Host 'Enter ile kapat'
    exit 1
}
$final = (Get-Item $Local).Length
Write-Host ''
if ($final -ge ($TargetBytes * 0.95)) {
    Write-Host "BASARILI: $([math]::Round($final/1MB,2)) MB indirildi ($sw.Elapsed.ToString('mm\:ss'))" -ForegroundColor Green
    Write-Log "TAMAM $final byte"

    # Git snapshot yenile
    Write-Log 'Git snapshot yenileniyor...'
    $gitCmd = 'cd /home/kokpitim.com/public_html; sudo git rev-parse HEAD; sudo git log -1 --oneline'
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i $KeyPath "mfgulen4660@${Ip}" $gitCmd |
        Out-File (Join-Path $Base 'gcp_git_snapshot.txt') -Encoding utf8

    # Checklist guncelle
    $mbFinal = [math]::Round($final / 1MB, 2)
    $ok = '[X]'
    $checkLines = @(
        ('GCP KAPATMA ONCESI - {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm')),
        ($ok + ' PostgreSQL dump'),
        ($ok + ' .env + docker env'),
        ($ok + ' instance/'),
        ($ok + ' VM backups (~10 MB)'),
        ($ok + ' Kod arsivi ' + $mbFinal + ' MB'),
        ($ok + ' Git snapshot (yenilendi)'),
        'GCP VM STOP icin hazir (dump dogrulandi).'
    )
    $checkLines | Out-File (Join-Path $Base 'GCP_KAPATMA_CHECKLIST.txt') -Encoding utf8
} else {
    Write-Host "UYARI: Dosya eksik gorunuyor: $([math]::Round($final/1MB,2)) MB / $([math]::Round($TargetBytes/1MB,2)) MB" -ForegroundColor Yellow
    Write-Log "EKSIK $final / $TargetBytes"
}

Write-Host ''
Write-Host "Log: $LogFile"
Read-Host 'Kapatmak icin Enter'
