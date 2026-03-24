param(
    [string]$Instance = "sps-server-v2",
    [string]$Zone = "europe-west3-c",
    [string]$VmAppDir = "/home/kokpitim.com/public_html",
    [string]$BackupDir = "/home/kokpitim.com/public_html/backups",
    [string]$PgDatabase = "kokpitim_db",
    [string]$HealthUrl = "http://127.0.0.1/health",
    [switch]$ShowDockerLogs
)

$ErrorActionPreference = "Stop"

function Invoke-VMCommand {
    param([Parameter(Mandatory = $true)][string]$Command)
    gcloud compute ssh $Instance --zone $Zone --command $Command
}

function Get-PgCount {
    param([Parameter(Mandatory = $true)][string]$TableName)
    $cmd = "sudo -u postgres psql -d '$PgDatabase' -tAc 'select count(1) from $TableName'"
    $raw = Invoke-VMCommand -Command $cmd | Out-String
    $v = ($raw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
    if (-not $v) { return "N/A" }
    return [int]$v
}

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$pgBackup = "kokpitim_pg_smoke_$ts.sql"
$sqliteBackup = "kokpitim_sqlite_smoke_$ts.db"

Write-Host "==> 1/4 VM backup aliniyor..." -ForegroundColor Cyan
Invoke-VMCommand -Command "mkdir -p '$BackupDir'"
Invoke-VMCommand -Command "sudo -u postgres pg_dump '$PgDatabase' > /tmp/$pgBackup && sudo cp /tmp/$pgBackup '$BackupDir/'"
Invoke-VMCommand -Command "if [ -f '$VmAppDir/instance/kokpitim.db' ]; then sudo cp '$VmAppDir/instance/kokpitim.db' '$BackupDir/$sqliteBackup'; fi"

Write-Host "==> 2/4 Health kontrolu..." -ForegroundColor Cyan
$health = Invoke-VMCommand -Command "curl -s '$HealthUrl'"
Write-Host $health

Write-Host "==> 3/4 Temel veri sayilari..." -ForegroundColor Cyan
$metrics = @(
    @{ Name = "Kurum"; Table = "tenants" },
    @{ Name = "Kullanici"; Table = "users" },
    @{ Name = "Surec"; Table = "processes" },
    @{ Name = "PG"; Table = "process_kpis" },
    @{ Name = "PGV"; Table = "kpi_data" },
    @{ Name = "Surec_Faaliyeti"; Table = "process_activities" },
    @{ Name = "Proje"; Table = "project" },
    @{ Name = "Proje_Faaliyeti"; Table = "task" }
)

$rows = foreach ($m in $metrics) {
    [PSCustomObject]@{
        Metrik = $m.Name
        Tablo  = $m.Table
        Adet   = Get-PgCount -TableName $m.Table
    }
}
$rows | Format-Table -AutoSize

Write-Host "==> 4/4 Servis ve port kontrolu..." -ForegroundColor Cyan
Invoke-VMCommand -Command "sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
Invoke-VMCommand -Command "ss -ltn | sed -n '1,20p'"

if ($ShowDockerLogs) {
    Write-Host "==> Docker log (son 120 satir)" -ForegroundColor Yellow
    Invoke-VMCommand -Command "sudo docker logs sps-web --tail=120"
}

Write-Host ""
Write-Host "Tamamlandi." -ForegroundColor Green
Write-Host "PostgreSQL backup: $BackupDir/$pgBackup"
Write-Host "SQLite backup:     $BackupDir/$sqliteBackup"
