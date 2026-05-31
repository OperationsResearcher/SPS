# VM (Oracle) kod + PostgreSQL yedeğini yerele indirir.
# Kullanım:
#   .\scripts\ops\oracle\vm_pull_to_local.ps1
#   .\scripts\ops\oracle\vm_pull_to_local.ps1 -SkipVmBackup   # VM'de yedek zaten varsa

param(
    [string]$OracleHost = '129.159.30.175',
    [string]$OracleUser = 'ubuntu',
    [string]$IdentityFile = 'C:\crt\ssh-key-2026-04-18_v4.key',
    [string]$OutRoot = 'C:\kokpitim\backups\vm_pull',
    [switch]$SkipVmBackup
)

$ErrorActionPreference = 'Stop'
$sshTarget = "${OracleUser}@${OracleHost}"
$sshArgs = @('-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=30', '-i', $IdentityFile)

function Invoke-OracleSsh([string]$Cmd) {
    & ssh.exe @sshArgs $sshTarget $Cmd
    if ($LASTEXITCODE -ne 0) { throw "SSH failed" }
}

function Invoke-OracleScp([string]$Remote, [string]$Local) {
    & scp.exe @sshArgs $Remote $Local
    if ($LASTEXITCODE -ne 0) { throw "SCP failed: $Remote" }
}

New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

if (-not $SkipVmBackup) {
    Write-Host '==> VM uzerinde tam yedek (kod + PG + instance)' -ForegroundColor Cyan
    $localScript = Join-Path $PSScriptRoot 'oracle_full_backup.sh'
    & scp.exe @sshArgs $localScript "${sshTarget}:/tmp/oracle_full_backup.sh"
    Invoke-OracleSsh "sed -i 's/\r$//' /tmp/oracle_full_backup.sh && sudo bash /tmp/oracle_full_backup.sh"
}

$remoteDir = (Invoke-OracleSsh "ls -td /opt/kokpitim/backups/full_* 2>/dev/null | head -1").Trim()
if (-not $remoteDir) { throw 'VM yedek dizini bulunamadi' }
$ts = Split-Path $remoteDir -Leaf
$localDir = Join-Path $OutRoot $ts
New-Item -ItemType Directory -Force -Path $localDir | Out-Null

Write-Host "==> Indiriliyor: $remoteDir -> $localDir" -ForegroundColor Cyan
Invoke-OracleSsh "sudo chmod -R a+rX $remoteDir"

$files = @(
    'pg_kokpitim_db.dump.gz',
    'pg_kokpitim_db.sql.gz',
    'instance.tar.gz',
    'manifest.txt',
    'git_snapshot.txt',
    'env_snapshot.txt',
    'alembic_version.txt',
    'app_code.tar.gz'
)
foreach ($f in $files) {
    Write-Host "  $f ..."
    Invoke-OracleScp "${sshTarget}:${remoteDir}/${f}" (Join-Path $localDir $f)
}

$readme = @"
VM yedek — $ts
Kaynak: $OracleHost
Git: $(Get-Content (Join-Path $localDir 'git_snapshot.txt') -Raw -ErrorAction SilentlyContinue)

Dosyalar:
  pg_kokpitim_db.dump.gz  — pg_restore ile restore
  pg_kokpitim_db.sql.gz   — psql/gunzip fallback
  app_code.tar.gz         — /opt/kokpitim/app ( .git haric )
  instance.tar.gz         — /opt/kokpitim/instance
  env_snapshot.txt        — HASSAS — Git'e koymayin

Yerel restore (ornek):
  pg_restore -h localhost -U kokpitim_user -d kokpitim_db --clean --if-exists pg_kokpitim_db.dump.gz
"@
$readme | Out-File (Join-Path $localDir 'README_YEREL.txt') -Encoding utf8

Write-Host ''
Write-Host 'TAMAM' -ForegroundColor Green
Get-ChildItem $localDir | Format-Table Name, @{n='MB';e={[math]::Round($_.Length/1MB,2)}} -AutoSize
Write-Host "Konum: $localDir"
