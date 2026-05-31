# Yerelden Oracle'a deploy paketi yukle + bootstrap
# Kullanim:
#   .\scripts\ops\oracle\oracle_deploy.ps1 -IdentityFile C:\Users\YOU\.ssh\id_rsa
param(
    [string]$OracleHost = '129.159.30.175',
    [string]$OracleUser = 'ubuntu',
    [string]$IdentityFile = 'C:\crt\ssh-key-2026-04-18_v4.key',
    [string]$GitRef = '53334f44fb8216fc5398e977cf073146ac93c8a6'
)

$ErrorActionPreference = 'Stop'
$Root = 'C:\kokpitim'
$Migration = Join-Path $Root 'backups\oracle_migration'
$Staging = Join-Path $Migration 'deploy_staging'
$Bootstrap = Join-Path $Root 'scripts\ops\oracle\oracle_server_bootstrap.sh'

if (-not $IdentityFile) {
    foreach ($c in @(
            "$env:USERPROFILE\.ssh\id_rsa",
            "$env:USERPROFILE\.ssh\id_ed25519",
            "$env:USERPROFILE\.ssh\oracle",
            "$env:USERPROFILE\.ssh\kokpitim_oracle"
        )) {
        if (Test-Path $c) { $IdentityFile = $c; break }
    }
}
if (-not $IdentityFile -or -not (Test-Path $IdentityFile)) {
    Write-Host 'HATA: Oracle SSH private key gerekli.' -ForegroundColor Red
    Write-Host 'Ornek: .\scripts\ops\oracle\oracle_deploy.ps1 -IdentityFile C:\Users\YOU\.ssh\ANAHTAR'
    exit 1
}

$sshBase = @('-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=30', '-i', $IdentityFile)
function Invoke-OracleSsh([string]$cmd) {
    & ssh.exe @sshBase "${OracleUser}@${OracleHost}" $cmd
    if ($LASTEXITCODE -ne 0) { throw "SSH failed: $cmd" }
}
function Send-OracleScp([string]$local, [string]$remote) {
    & scp.exe @sshBase $local "${OracleUser}@${OracleHost}:${remote}"
    if ($LASTEXITCODE -ne 0) { throw "SCP failed: $local" }
}

Write-Host '==> Staging paketi hazirlaniyor...' -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $Staging | Out-Null

$dump = Get-ChildItem $Migration -Filter 'kokpitim_db*.dump' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $dump) { throw 'Dump bulunamadi: backups/oracle_migration/kokpitim_db*.dump' }
Copy-Item $dump.FullName (Join-Path $Staging 'kokpitim_db.dump') -Force

$instTar = Get-ChildItem $Migration -Filter 'kokpitim_instance*.tar.gz' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($instTar) {
    Copy-Item $instTar.FullName (Join-Path $Staging 'instance.tar.gz') -Force
} elseif (Test-Path (Join-Path $Migration 'instance')) {
    & tar -czf (Join-Path $Staging 'instance.tar.gz') -C $Migration instance
}

# Production .env (GCP docker env'den)
$envContent = @"
SECRET_KEY=e8f4c2a1b9d7e6f3a2c8b4d9e1f7a3c5b8d2e6f9a1c4d7e2f8b3c6d9e4f1a7c2
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://kokpitim_user:MfGMfG__46604660@host.docker.internal:5432/kokpitim_db
FLASK_ENV=production
TRUST_PROXY=1
RATELIMIT_STORAGE_URL=memory://
HGS_BYPASS_ENABLED=false
GEMINI_API_KEY=AIzaSyD7ufB4lBkiygJ1VmNb3_WzaNfVbo80WL4
"@
$envContent | Out-File (Join-Path $Staging '.env') -Encoding ascii -NoNewline
"KOKPITIM_DB_PASSWORD=MfGMfG__46604660" | Out-File (Join-Path $Staging 'oracle_db.env') -Encoding ascii

Write-Host '==> Oracle SSH test...' -ForegroundColor Cyan
Invoke-OracleSsh "echo ORACLE_OK; hostname; df -h / | tail -1"

Write-Host '==> Dosyalar yukleniyor (birkaç dakika)...' -ForegroundColor Cyan
Invoke-OracleSsh 'mkdir -p /tmp/kokpitim_deploy'
Get-ChildItem $Staging -File | ForEach-Object {
    Write-Host "  SCP $($_.Name) ($([math]::Round($_.Length/1MB,2)) MB)"
    Send-OracleScp $_.FullName "/tmp/kokpitim_deploy/$($_.Name)"
}
Send-OracleScp $Bootstrap '/tmp/kokpitim_deploy/oracle_server_bootstrap.sh'
Invoke-OracleSsh 'chmod +x /tmp/kokpitim_deploy/oracle_server_bootstrap.sh'

Write-Host "==> Bootstrap (git ref: $GitRef)..." -ForegroundColor Cyan
Invoke-OracleSsh "export GIT_REF='$GitRef'; bash /tmp/kokpitim_deploy/oracle_server_bootstrap.sh"

Write-Host ''
Write-Host 'TAMAM. Sonraki adimlar:' -ForegroundColor Green
Write-Host '  1) Oracle: curl http://127.0.0.1:8088/health'
Write-Host '  2) certbot: sudo certbot --nginx -d www.kokpitim.com -d kokpitim.com'
Write-Host '  3) Cloudflare DNS www -> 129.159.30.175'
Write-Host '  4) docs/gcp2oraclegecisplani.md Faz 5-7'
