#Requires -Version 5.1
<#
.SYNOPSIS
  Yerel → Test (sıfırdan) → Yayın deploy orchestrator (token-ucuz yol).

.DESCRIPTION
  Bağlayıcı kurallar: docs/SUNUCU-GUNCELLEME-REHBERI.md
  Başarısız adımda FALLBACK basar → geleneksel elle yola düşülür.

.PARAMETER Mod
  hepsi   = 4-katman + Test sıfırdan + Yayın deploy + seed (varsayılan)
  kontrol = yalnız 4-katman raporu (yazmaz)
  test    = yalnız Test sıfırdan
  yayin   = yalnız Yayın (oracle_safe_deploy + seed)

.PARAMETER Onay
  Yıkıcı adımlar (Test wipe / Yayın deploy) için ZORUNLU.

.EXAMPLE
  .\scripts\ops\oracle\yayina_ver.ps1 -Mod kontrol
  .\scripts\ops\oracle\yayina_ver.ps1 -Mod hepsi -Onay
  .\scripts\ops\oracle\yayina_ver.ps1 -Mod yayin -Onay -AtlaTest
#>
param(
    [ValidateSet('hepsi', 'kontrol', 'test', 'yayin')]
    [string]$Mod = 'hepsi',

    [switch]$Onay,
    [switch]$AtlaTest,
    [switch]$AtlaSeed,
    [switch]$AtlaPushKontrol,

    [string]$OracleHost = '129.159.30.175',
    [string]$OracleUser = 'ubuntu',
    [string]$IdentityFile = 'C:\crt\ssh-key-2026-04-18_v4.key',
    [string]$RepoRoot = 'C:\kokpitim',
    [string]$PgDump = 'C:\pgdata\bin\pg_dump.exe',
    [string]$LocalDbName = 'kokpitim_db',
    [string]$LocalDbUser = 'kokpitim_user'
)

$ErrorActionPreference = 'Stop'
$Key = $IdentityFile
$SshTarget = "${OracleUser}@${OracleHost}"
$SshOpts = @('-i', $Key, '-o', 'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=30', '-o', 'ConnectTimeout=20')
$RemoteOps = '/opt/kokpitim/app/scripts/ops/oracle'
$TmpDumpSql = 'C:\tmp\kokpitim_db_local.sql'
$TmpDumpGz = 'C:\tmp\kokpitim_db_local.sql.gz'

function Write-Banner([string]$msg) {
    Write-Host ""
    Write-Host ("=" * 64) -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host ("=" * 64) -ForegroundColor Cyan
}

function Write-Fallback([string]$step, [string]$detail = '') {
    Write-Host ""
    Write-Host "FALLBACK — script durdu: $step" -ForegroundColor Red
    if ($detail) { Write-Host $detail -ForegroundColor Yellow }
    Write-Host @"

Geleneksel yol (canonical):
  docs/SUNUCU-GUNCELLEME-REHBERI.md  §3 yedek · §4 Yayın · §0.6/§5 Test sıfırdan

Elle Yayın:
  ssh -i $IdentityFile $SshTarget
  cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
  sudo docker exec kokpitim-web bash -lc 'cd /app && python3 scripts/seed_card_descriptions.py --calistir'

Elle Test: rehber §0.6 — container+DB+kod sil, yerel dump + rebuild.
Ajan kuralı: script çözemezse geleneksel yolla devam; sessiz yama yok.
"@ -ForegroundColor Yellow
}

function Invoke-Oracle([string]$RemoteCmd) {
    & ssh.exe @SshOpts $SshTarget $RemoteCmd
    return $LASTEXITCODE
}

function Send-File([string]$Local, [string]$Remote) {
    & scp.exe @SshOpts -C $Local "${SshTarget}:${Remote}"
    if ($LASTEXITCODE -ne 0) { throw "SCP failed: $Local -> $Remote (exit $LASTEXITCODE)" }
}

function Ensure-LfScript([string]$Path) {
    $raw = [IO.File]::ReadAllText($Path)
    $lf = $raw -replace "`r`n", "`n" -replace "`r", "`n"
    if ($lf -ne $raw) {
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [IO.File]::WriteAllText($Path, $lf, $utf8NoBom)
    }
}

function Sync-RemoteOpsScripts {
    # Scriptler henüz Yayın'da eski commit'teyse /tmp'ye kopyala (küçük dosya — scp güvenli)
    $files = @(
        'lib_yayin_common.sh',
        'dort_katman_kontrol.sh',
        'test_sifirdan.sh',
        'yayin_seed_kart.sh',
        'oracle_safe_deploy.sh'
    )
    $localDir = Join-Path $RepoRoot 'scripts\ops\oracle'
    foreach ($f in $files) {
        $p = Join-Path $localDir $f
        if (-not (Test-Path $p)) { throw "Eksik script: $p" }
        Ensure-LfScript $p
        Send-File $p "/tmp/$f"
    }
    $null = Invoke-Oracle 'chmod +x /tmp/*.sh 2>/dev/null; mkdir -p /tmp/kokpitim_ops && cp -f /tmp/lib_yayin_common.sh /tmp/dort_katman_kontrol.sh /tmp/test_sifirdan.sh /tmp/yayin_seed_kart.sh /tmp/oracle_safe_deploy.sh /tmp/kokpitim_ops/ && chmod +x /tmp/kokpitim_ops/*.sh'
}

function Get-LocalMainSha {
    Push-Location $RepoRoot
    try {
        return (git rev-parse HEAD).Trim()
    }
    finally { Pop-Location }
}

function Assert-MainPushed {
    if ($AtlaPushKontrol) {
        Write-Host 'UYARI: push kontrolü atlandı (-AtlaPushKontrol)' -ForegroundColor Yellow
        return
    }
    Push-Location $RepoRoot
    try {
        git fetch origin main 2>$null | Out-Null
        $local = (git rev-parse HEAD).Trim()
        $remote = (git rev-parse origin/main).Trim()
        if ($local -ne $remote) {
            Write-Fallback 'git-push' "Yerel HEAD ($local) != origin/main ($remote). Önce: git push origin main"
            exit 10
        }
        $branch = (git branch --show-current).Trim()
        if ($branch -ne 'main') {
            Write-Host "UYARI: branch=$branch (main değil). origin/main ile eşit SHA var; devam." -ForegroundColor Yellow
        }
        Write-Host "OK: origin/main = $remote"
    }
    finally { Pop-Location }
}

function Get-LocalDbPassword {
    $envPath = Join-Path $RepoRoot '.env'
    if (-not (Test-Path $envPath)) { throw '.env yok' }
    $line = Get-Content $envPath | Where-Object { $_ -match '^\s*SQLALCHEMY_DATABASE_URI=' } | Select-Object -First 1
    if (-not $line) { throw 'SQLALCHEMY_DATABASE_URI .env içinde yok' }
    # postgresql+psycopg2://user:pass@host/db
    if ($line -match '://[^:]+:([^@]+)@') { return $Matches[1] }
    throw 'DB şifresi URI''den okunamadı'
}

function New-LocalDumpGz {
    Write-Banner 'Yerel PG dump (Test için)'
    if (-not (Test-Path $PgDump)) {
        Write-Fallback 'pg_dump' "Bulunamadı: $PgDump (PG18 C:\pgdata\bin kullan)"
        exit 11
    }
    New-Item -ItemType Directory -Force -Path 'C:\tmp' | Out-Null
    Remove-Item $TmpDumpSql, $TmpDumpGz -Force -ErrorAction SilentlyContinue
    $env:PGPASSWORD = Get-LocalDbPassword
    try {
        & $PgDump -h localhost -U $LocalDbUser -d $LocalDbName -Fp -f $TmpDumpSql
        if ($LASTEXITCODE -ne 0) { throw "pg_dump exit $LASTEXITCODE" }
    }
    finally { Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue }

    $in = [IO.File]::OpenRead($TmpDumpSql)
    $out = [IO.File]::Create($TmpDumpGz)
    $gz = New-Object IO.Compression.GZipStream($out, [IO.Compression.CompressionMode]::Compress)
    try { $in.CopyTo($gz) }
    finally { $gz.Dispose(); $out.Dispose(); $in.Dispose() }

    $mb = [math]::Round((Get-Item $TmpDumpGz).Length / 1MB, 2)
    Write-Host "Dump gzip: $TmpDumpGz ($mb MB)"
    if ($mb -lt 1) {
        Write-Fallback 'dump-size' "Gzip şüpheli küçük ($mb MB) — dump bozuk olabilir"
        exit 12
    }
}

function Send-DumpWithRetry {
    $max = 3
    for ($i = 1; $i -le $max; $i++) {
        Write-Host "SCP dump deneme $i/$max ..."
        try {
            Send-File $TmpDumpGz '/tmp/kokpitim_db_local.sql.gz'
            $localHash = (Get-FileHash $TmpDumpGz -Algorithm MD5).Hash.ToLower()
            $remoteLine = & ssh.exe @SshOpts $SshTarget 'md5sum /tmp/kokpitim_db_local.sql.gz'
            $remoteHash = ($remoteLine -split '\s+')[0].ToLower()
            if ($localHash -ne $remoteHash) { throw "MD5 mismatch local=$localHash remote=$remoteHash" }
            Write-Host "OK: dump MD5 $localHash"
            return
        }
        catch {
            Write-Host "SCP hata: $_" -ForegroundColor Yellow
            if ($i -eq $max) {
                Write-Fallback 'scp-dump' "Dump scp $max denemede başarısız. Elle: scp -C $TmpDumpGz ${SshTarget}:/tmp/"
                exit 13
            }
            Start-Sleep -Seconds 5
        }
    }
}

function Invoke-DortKatman([string]$ExpectedSha) {
    Write-Banner '4 katman kontrol (Yayın)'
    # Önce /tmp kopyası (eski Yayın commit'inde script yoksa)
    $code = Invoke-Oracle "bash /tmp/kokpitim_ops/dort_katman_kontrol.sh $ExpectedSha"
    if ($code -ne 0) {
        Write-Fallback '4-katman' "exit $code"
        exit $code
    }
}

function Invoke-TestSifirdan {
    Write-Banner 'Test sıfırdan'
    $code = Invoke-Oracle 'sudo DUMP=/tmp/kokpitim_db_local.sql.gz bash /tmp/kokpitim_ops/test_sifirdan.sh'
    if ($code -ne 0) {
        Write-Fallback 'test_sifirdan' "exit $code — docker logs / restore log'a bak"
        exit $code
    }
}

function Invoke-YayinDeploy {
    Write-Banner 'Yayın oracle_safe_deploy (yedek + pull + build + alembic)'
    # Deploy sonrası scriptler app içinde güncellenir; önce mevcut app scriptini dene, yoksa /tmp
    $code = Invoke-Oracle @'
set -e
if [ -f /opt/kokpitim/app/scripts/ops/oracle/oracle_safe_deploy.sh ]; then
  cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/oracle_safe_deploy.sh
else
  sudo bash /tmp/kokpitim_ops/oracle_safe_deploy.sh
fi
'@
    if ($code -ne 0) {
        Write-Fallback 'oracle_safe_deploy' "exit $code — yedek /opt/kokpitim/backups/ altında"
        exit $code
    }
}

function Invoke-YayinSeed {
    Write-Banner 'Yayın kart seed'
    # Deploy sonrası app içindeki güncel script tercih
    $code = Invoke-Oracle @'
set -e
if [ -f /opt/kokpitim/app/scripts/ops/oracle/yayin_seed_kart.sh ]; then
  cd /opt/kokpitim/app && sudo bash scripts/ops/oracle/yayin_seed_kart.sh
else
  sudo bash /tmp/kokpitim_ops/yayin_seed_kart.sh
fi
'@
    if ($code -ne 0) {
        Write-Fallback 'yayin_seed' "exit $code"
        exit $code
    }
}

# --- main ---
Write-Banner "yayina_ver.ps1 — Mod=$Mod"

if (-not (Test-Path $Key)) {
    Write-Fallback 'ssh-key' "Anahtar yok: $Key"
    exit 1
}

$needDestructive = $Mod -in @('hepsi', 'test', 'yayin')
if ($needDestructive -and -not $Onay) {
    Write-Host 'Yıkıcı adım için -Onay gerekli. Örnek:' -ForegroundColor Yellow
    Write-Host '  .\scripts\ops\oracle\yayina_ver.ps1 -Mod hepsi -Onay'
    Write-Host 'Yalnız rapor: .\scripts\ops\oracle\yayina_ver.ps1 -Mod kontrol'
    exit 9
}

Assert-MainPushed
$sha = Get-LocalMainSha
Write-Host "Hedef SHA: $sha"

try {
    Sync-RemoteOpsScripts
}
catch {
    Write-Fallback 'script-sync' "$_"
    exit 14
}

switch ($Mod) {
    'kontrol' {
        Invoke-DortKatman $sha
        Write-Host 'Kontrol bitti (yazma yok).' -ForegroundColor Green
        break
    }
    'test' {
        New-LocalDumpGz
        Send-DumpWithRetry
        Invoke-DortKatman $sha
        Invoke-TestSifirdan
        break
    }
    'yayin' {
        Invoke-DortKatman $sha
        Invoke-YayinDeploy
        if (-not $AtlaSeed) { Invoke-YayinSeed }
        Invoke-DortKatman $sha
        break
    }
    'hepsi' {
        Invoke-DortKatman $sha
        if (-not $AtlaTest) {
            New-LocalDumpGz
            Send-DumpWithRetry
            Invoke-TestSifirdan
        }
        else {
            Write-Host 'Test atlandı (-AtlaTest) — kural dışı; bilinçli.' -ForegroundColor Yellow
        }
        Invoke-YayinDeploy
        if (-not $AtlaSeed) { Invoke-YayinSeed }
        else { Write-Host 'Seed atlandı (-AtlaSeed)' -ForegroundColor Yellow }
        Invoke-DortKatman $sha
        Write-Host ''
        Write-Host 'TAMAM — Test+Yayın akışı bitti. seed_calistirma_kaydi.md + TASKLOG güncelle.' -ForegroundColor Green
        break
    }
}

Write-Host ''
Write-Host 'Not: Redis yoksa oracle_safe_deploy UYARI basar (bilinen). Demo bu scriptte yok.' -ForegroundColor DarkGray
