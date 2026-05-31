# VM acil PostgreSQL yedek cekme (billing acik + VM RUNNING olmali)
# Kullanim:
#   cd C:\kokpitim
#   .\scripts\ops\vm_emergency_pull_db.ps1
param(
    [string]$ProjectId = "project-ab214714-b5d6-43db-b33",
    [string]$Zone = "europe-west3-c",
    [string]$Instance = "sps-server-v2",
    [string]$OutDir = "C:\kokpitim\backups\vm_emergency"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Get-GcpAccessToken {
    $adcPath = Join-Path $env:APPDATA "gcloud\legacy_credentials\mfgulen4660@gmail.com\adc.json"
    if (-not (Test-Path $adcPath)) {
        throw "adc.json bulunamadi. Once: gcloud auth login"
    }
    $adc = Get-Content $adcPath | ConvertFrom-Json
    $body = @{
        client_id     = $adc.client_id
        client_secret = $adc.client_secret
        refresh_token = $adc.refresh_token
        grant_type    = "refresh_token"
    }
    $tok = Invoke-RestMethod -Uri "https://oauth2.googleapis.com/token" -Method Post -Body $body
    return $tok.access_token
}

function Invoke-GcpApi {
    param([string]$Url, [string]$Token)
    $headers = @{ Authorization = "Bearer $Token" }
    return Invoke-RestMethod -Uri $Url -Headers $headers -Method Get
}

Write-Host "==> 1/5 Billing kontrolu"
$token = Get-GcpAccessToken
$billing = Invoke-GcpApi -Url "https://cloudbilling.googleapis.com/v1/projects/$ProjectId/billingInfo" -Token $token
if (-not $billing.billingEnabled) {
    Write-Host ""
    Write-Host "HATA: GCP billing KAPALI (billingEnabled=false)." -ForegroundColor Red
    Write-Host "Console: https://console.cloud.google.com/billing/linkedaccount?project=$ProjectId"
    Write-Host "Billing acmadan VM baslatilamaz ve taze DB cekilemez."
    Write-Host "Disk verisi genelde duruyor; billing ac -> VM start -> bu betigi tekrar calistir."
    exit 2
}
Write-Host "Billing: ACIK"

Write-Host "==> 2/5 VM durumu"
$vmUrl = "https://compute.googleapis.com/compute/v1/projects/$ProjectId/zones/$Zone/instances/$Instance"
try {
    $vm = Invoke-GcpApi -Url $vmUrl -Token $token
} catch {
    Write-Host "Compute API hatasi: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Console'dan VM durumunu kontrol edin."
    exit 3
}

$status = $vm.status
$ip = $vm.networkInterfaces[0].accessConfigs[0].natIP
Write-Host "VM status: $status"
Write-Host "External IP: $ip"

if ($status -ne "RUNNING") {
    Write-Host ""
    Write-Host "HATA: VM calismiyor ($status)." -ForegroundColor Red
    Write-Host "Console: https://console.cloud.google.com/compute/instances?project=$ProjectId"
    Write-Host "VM'i START edin, 1-2 dk bekleyin, betigi tekrar calistirin."
    exit 4
}

Write-Host "==> 3/5 VM'de pg_dump"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$remoteDump = "/tmp/kokpitim_db_emergency_${ts}.dump"
$sshKey = Join-Path $env:USERPROFILE ".ssh\google_compute_engine"
if (-not (Test-Path $sshKey)) {
    Write-Host "SSH key yok: $sshKey" -ForegroundColor Red
    Write-Host "Alternatif: Console -> VM -> SSH (tarayici) ile baglanip su komutu calistirin:"
    Write-Host "  sudo -u postgres pg_dump -Fc kokpitim_db > $remoteDump && sudo chmod a+r $remoteDump"
    exit 5
}

$sshUser = "mfgulen4660"
$remoteCmd = "sudo -u postgres pg_dump -Fc kokpitim_db > $remoteDump && sudo chmod a+r $remoteDump && ls -lah $remoteDump"
& ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -i $sshKey "${sshUser}@${ip}" $remoteCmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "SSH/pg_dump basarisiz. Console SSH deneyin." -ForegroundColor Red
    exit 6
}

Write-Host "==> 4/5 Yerel indirme (scp)"
$localDump = Join-Path $OutDir "kokpitim_db_emergency_${ts}.dump"
& scp -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i $sshKey "${sshUser}@${ip}:${remoteDump}" $localDump
if ($LASTEXITCODE -ne 0) {
    Write-Host "SCP basarisiz." -ForegroundColor Red
    exit 7
}

Write-Host "==> 5/5 Ozet"
Get-Item $localDump | Format-List FullName, Length, LastWriteTime
Write-Host "Tamamlandi. Restore ornegi:"
Write-Host "  pg_restore -U postgres -d kokpitim_local --clean --if-exists `"$localDump`""
