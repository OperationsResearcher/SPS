# GCP VM tam yedek cekme (kapatmadan once)
param(
    [string]$Ip = '35.246.135.36',
    [string]$OutDir = 'C:\kokpitim\backups\oracle_migration',
    [string]$KeyPath = "$env:TEMP\kokpitim_vm_temp_key"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir, "$OutDir\env", "$OutDir\gcp_vm_backups" | Out-Null

function Invoke-Ssh([string]$Cmd) {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=60 -i $KeyPath "mfgulen4660@$Ip" $Cmd
}

Write-Host "==> 1/6 Git commit kaydi"
$gitInfo = Invoke-Ssh "cd /home/kokpitim.com/public_html && sudo git rev-parse HEAD && sudo git log -1 --oneline && sudo git status -sb"
$gitInfo | Out-File "$OutDir\gcp_git_snapshot.txt" -Encoding utf8

Write-Host "==> 2/6 Docker sps-web env (inspect)"
Invoke-Ssh "sudo docker inspect sps-web --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null || echo '# container yok'" |
    Out-File "$OutDir\env\docker_sps-web_env.txt" -Encoding utf8

Write-Host "==> 3/6 VM backups/ klasoru tar"
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$remoteBackups = "/tmp/kokpitim_gcp_backups_${ts}.tar.gz"
Invoke-Ssh "sudo tar czf $remoteBackups -C /home/kokpitim.com/public_html backups && sudo chmod a+r $remoteBackups && ls -lah $remoteBackups"
$localBackups = Join-Path $OutDir "kokpitim_gcp_backups_${ts}.tar.gz"
scp -o StrictHostKeyChecking=no -o ConnectTimeout=300 -i $KeyPath "mfgulen4660@${Ip}:${remoteBackups}" $localBackups
Invoke-Ssh "sudo rm -f $remoteBackups"

Write-Host "==> 4/6 Kod arsivi (491MB) - uzun surebilir"
$remoteCode = '/tmp/kokpitim_code_20260521_215500.tar.gz'
$localCode = Join-Path $OutDir 'kokpitim_code_20260521_215500.tar.gz'
Invoke-Ssh "ls -lah $remoteCode || (sudo tar czf $remoteCode -C /home/kokpitim.com/public_html --exclude=backups --exclude=instance --exclude=.git --exclude=__pycache__ --exclude=.venv . && sudo chmod a+r $remoteCode && ls -lah $remoteCode)"
if (Test-Path $localCode) { Remove-Item $localCode -Force }
scp -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ConnectTimeout=900 -i $KeyPath "mfgulen4660@${Ip}:${remoteCode}" $localCode
$codeSize = (Get-Item $localCode).Length
if ($codeSize -lt 400000000) { throw "Kod arsivi eksik: $codeSize byte (hedef ~515MB)" }
Invoke-Ssh "sudo rm -f $remoteCode /tmp/kokpitim_instance_*.tar.gz"

Write-Host "==> 5/6 Taze pg_dump"
$remoteDump = "/tmp/kokpitim_db_final_${ts}.dump"
$localDump = Join-Path $OutDir "kokpitim_db_final_${ts}.dump"
Invoke-Ssh "sudo -u postgres pg_dump -Fc kokpitim_db > $remoteDump && sudo chmod a+r $remoteDump && ls -lah $remoteDump"
scp -o StrictHostKeyChecking=no -o ConnectTimeout=120 -i $KeyPath "mfgulen4660@${Ip}:${remoteDump}" $localDump
Invoke-Ssh "sudo rm -f $remoteDump"

Write-Host "==> 6/6 Ozet"
Get-ChildItem $OutDir -File | Sort-Object Length -Descending | Format-Table Name, @{n='MB';e={[math]::Round($_.Length/1MB,2)}} -AutoSize
Write-Host "TAMAM"
