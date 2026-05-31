# GCP kapatmadan once TAM yedek — PowerShell'de calistirin (10-20 dk surebilir)
#   cd C:\kokpitim
#   .\scripts\ops\gcp_full_pull_manual.ps1
$ErrorActionPreference = 'Stop'
$KeyPath = "$env:TEMP\kokpitim_vm_temp_key"
$Ip = '35.246.135.36'
$Base = 'C:\kokpitim\backups\oracle_migration'
New-Item -ItemType Directory -Force -Path $Base, "$Base\env" | Out-Null

function Ssh($cmd) {
    ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=15 -o ConnectTimeout=60 -i $KeyPath "mfgulen4660@$Ip" $cmd
}
function Scp-Remote($remote, $local) {
    if (Test-Path $local) { Remove-Item $local -Force }
    scp -o StrictHostKeyChecking=no -o ServerAliveInterval=15 -o ConnectTimeout=900 -i $KeyPath "mfgulen4660@${Ip}:${remote}" $local
    $len = (Get-Item $local).Length
    Write-Host "OK $local ($([math]::Round($len/1MB,2)) MB)"
    return $len
}

Write-Host "=== GCP TAM YEDEK ===" -ForegroundColor Cyan

# Git
Ssh "cd /home/kokpitim.com/public_html && sudo git rev-parse HEAD && sudo git log -1 --oneline" |
    Out-File "$Base\gcp_git_snapshot.txt" -Encoding utf8

# Docker env
Ssh "sudo docker inspect sps-web --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null" |
    Out-File "$Base\env\docker_sps-web_env.txt" -Encoding utf8

# .env (yenile)
Ssh "sudo cat /home/kokpitim.com/public_html/.env" | Out-File "$Base\env\.env" -Encoding utf8
Ssh "sudo test -f /home/kokpitim.com/public_html/.env.postgres && sudo cat /home/kokpitim.com/public_html/.env.postgres || echo '# yok'" |
    Out-File "$Base\env\.env.postgres" -Encoding utf8

# VM backups/ (~11 MB)
$rb = '/tmp/kokpitim_gcp_backups_20260521_220204.tar.gz'
Ssh "test -f $rb || (sudo tar czf $rb -C /home/kokpitim.com/public_html backups && sudo chmod a+r $rb); ls -lah $rb"
$lb = "$Base\kokpitim_gcp_backups_20260521_220204.tar.gz"
$bLen = Scp-Remote $rb $lb
if ($bLen -lt 10MB) { throw "backups eksik: $bLen" }

# Kod arsivi (~491 MB) — EN UZUN ADIM
$rc = '/tmp/kokpitim_code_20260521_215500.tar.gz'
Ssh "test -f $rc || (sudo tar czf $rc -C /home/kokpitim.com/public_html --exclude=backups --exclude=instance --exclude=.git --exclude=__pycache__ --exclude=.venv . && sudo chmod a+r $rc); ls -lah $rc"
$lc = "$Base\kokpitim_code_20260521_215500.tar.gz"
$cLen = Scp-Remote $rc $lc
if ($cLen -lt 400MB) { throw "kod arsivi eksik: $cLen byte (hedef ~515MB)" }

# Taze dump
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$rd = "/tmp/kokpitim_db_final_${ts}.dump"
$ld = "$Base\kokpitim_db_final_${ts}.dump"
Ssh "sudo -u postgres pg_dump -Fc kokpitim_db > $rd && sudo chmod a+r $rd && ls -lah $rd"
$dLen = Scp-Remote $rd $ld
if ($dLen -lt 500000) { throw "dump eksik: $dLen" }

# instance (yenile)
$ri = "/tmp/kokpitim_instance_refresh_${ts}.tar.gz"
Ssh "sudo tar czf $ri -C /home/kokpitim.com/public_html instance && sudo chmod a+r $ri && ls -lah $ri"
$li = "$Base\kokpitim_instance_refresh_${ts}.tar.gz"
Scp-Remote $ri $li | Out-Null
tar -xzf $li -C $Base --force

# Temizlik VM
Ssh "sudo rm -f $rb $rc $rd $ri /tmp/kokpitim_instance_*.tar.gz 2>/dev/null; echo VM tmp temiz"

# Checklist
$check = @"
GCP KAPATMA ONCESI KONTROL - $(Get-Date -Format 'yyyy-MM-dd HH:mm')
============================================================
[$(if($dLen -gt 500000){'X'}else{' '})] PostgreSQL dump (final + migration)
[$(if($cLen -gt 400MB){'X'}else{' '})] Kod arsivi ~491 MB
[$(if($bLen -gt 10MB){'X'}else{' '})] VM backups/ klasoru
[$(if(Test-Path "$Base\env\.env"){'X'}else{' '})] .env
[$(if(Test-Path "$Base\env\docker_sps-web_env.txt"){'X'}else{' '})] Docker container env
[$(if(Test-Path "$Base\instance"){'X'}else{' '})] instance/ (uploads)
[$(if(Test-Path "$Base\gcp_git_snapshot.txt"){'X'}else{' '})] Git commit: $(Get-Content "$Base\gcp_git_snapshot.txt" -TotalCount 1)

Git commit (canli):
$(Get-Content "$Base\gcp_git_snapshot.txt" -TotalCount 2)

Dosyalar:
$(Get-ChildItem $Base -File | ForEach-Object { "  $($_.Name) $([math]::Round($_.Length/1MB,2)) MB" })
"@
$check | Out-File "$Base\GCP_KAPATMA_CHECKLIST.txt" -Encoding utf8
Write-Host $check
Write-Host "`nTAMAM. Checklist: $Base\GCP_KAPATMA_CHECKLIST.txt" -ForegroundColor Green
