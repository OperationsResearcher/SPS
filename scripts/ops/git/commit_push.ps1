#Requires -Version 5.1
param(
    [ValidateSet('durum', 'commit')]
    [string]$Mod = 'durum',
    [string]$Mesaj = '',
    [switch]$Onay,
    [switch]$Push,
    [switch]$MainIzin,
    [switch]$TumunuEkle,
    [string]$YeniDal = '',
    [string]$Dal = '',
    [string]$RepoRoot = 'C:\kokpitim',
    [string]$Uzak = 'origin'
)
$ErrorActionPreference = 'Stop'
$SecretPatterns = @(
    '\.env$', '\.env\.', 'credentials\.json$', 'secret', '\.pem$',
    'id_rsa', 'id_ed25519', '\.p12$', '\.pfx$', 'oracle_db\.env$',
    'kokpitim_db.*\.sql$', 'kokpitim_db.*\.dump$', '\.sql\.gz$'
)
function Write-Banner([string]$m) {
    Write-Host ''
    Write-Host ('=' * 64) -ForegroundColor Cyan
    Write-Host "  $m" -ForegroundColor Cyan
    Write-Host ('=' * 64) -ForegroundColor Cyan
}
function Write-Fallback([string]$step, [string]$detail = '') {
    Write-Host ''
    Write-Host "FALLBACK - script durdu: $step" -ForegroundColor Red
    if ($detail) { Write-Host $detail -ForegroundColor Yellow }
    Write-Host ''
    Write-Host 'Geleneksel yol:' -ForegroundColor Yellow
    Write-Host '  git status -sb'
    Write-Host '  git diff'
    Write-Host '  git add PATHS'
    Write-Host '  git commit -m "mesaj"'
    Write-Host '  git push -u origin HEAD'
    Write-Host ''
    Write-Host 'GCM: pencereyi onayla. GIT_TERMINAL_PROMPT=0 / GCM_INTERACTIVE=never KULLANMA.' -ForegroundColor Yellow
    Write-Host 'Ajan: --no-verify / force-push YOK.' -ForegroundColor Yellow
}
function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    # git stdout'u PowerShell return degerine karismasin
    & git.exe -C $RepoRoot @GitArgs | Out-Host
    return [int]$LASTEXITCODE
}
function Test-SecretPath([string]$path) {
    $n = $path -replace '\\', '/'
    foreach ($pat in $SecretPatterns) {
        if ($n -match $pat) { return $true }
    }
    return $false
}
function Get-Branch {
    return (git -C $RepoRoot branch --show-current).Trim()
}
function Show-Durum {
    Write-Banner 'git durum'
    $null = Invoke-Git status -sb
    Write-Host ''
    Write-Host '--- staged ---' -ForegroundColor DarkGray
    $null = Invoke-Git diff --cached --stat
    Write-Host ''
    Write-Host '--- unstaged ---' -ForegroundColor DarkGray
    $null = Invoke-Git diff --stat
    Write-Host ''
    Write-Host '--- untracked (ozet) ---' -ForegroundColor DarkGray
    git -C $RepoRoot ls-files --others --exclude-standard | Select-Object -First 40
    $branch = Get-Branch
    Write-Host ''
    Write-Host "Dal: $branch"
    if ($branch -eq 'main') {
        Write-Host 'UYARI: main - commit icin -YeniDal veya -MainIzin.' -ForegroundColor Yellow
    }
}
function Ensure-Branch {
    if ($YeniDal) {
        $name = $YeniDal
        if ($name -notlike 'claude/*') { $name = "claude/$name" }
        Write-Host "Yeni dal: $name"
        $exists = git -C $RepoRoot branch --list $name
        if ($exists) { $code = Invoke-Git checkout $name }
        else { $code = Invoke-Git checkout -b $name }
        if ($code -ne 0) { Write-Fallback 'checkout-yeni-dal' "dal=$name exit=$code"; exit 20 }
        return
    }
    if ($Dal) {
        $code = Invoke-Git checkout $Dal
        if ($code -ne 0) { Write-Fallback 'checkout-dal' "dal=$Dal exit=$code"; exit 20 }
        return
    }
    $cur = Get-Branch
    if ($cur -eq 'main' -and -not $MainIzin) {
        Write-Fallback 'main-koruma' "main dogrudan commit yok. Ornek: -YeniDal ops-commit-push | istisna: -MainIzin"
        exit 21
    }
    if ($cur -eq 'main' -and $MainIzin) {
        Write-Host 'UYARI: -MainIzin ile main uzerinde commit' -ForegroundColor Yellow
    }
}
function Get-CandidateFiles {
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($line in (git -C $RepoRoot status --porcelain)) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $path = $line.Substring(3).Trim()
        if ($path -match ' -> ') { $path = ($path -split ' -> ')[-1] }
        $path = $path.Trim().Trim('"')
        if (-not [string]::IsNullOrWhiteSpace($path)) { [void]$out.Add($path) }
    }
    return $out | Select-Object -Unique
}
function Stage-Files {
    $cands = @(Get-CandidateFiles)
    if ($cands.Count -eq 0) {
        Write-Host 'Stage edilecek degisiklik yok.'
        return 0
    }
    $blocked = New-Object System.Collections.Generic.List[string]
    $ok = New-Object System.Collections.Generic.List[string]
    foreach ($p in $cands) {
        if (Test-SecretPath $p) { [void]$blocked.Add($p) } else { [void]$ok.Add($p) }
    }
    if ($blocked.Count -gt 0) {
        Write-Host 'SECRET atlandi (stage yok):' -ForegroundColor Yellow
        $blocked | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
    if ($ok.Count -eq 0) {
        Write-Fallback 'stage-bos' 'Yalniz secret adaylar veya degisiklik yok'
        exit 22
    }
    if ($TumunuEkle) {
        $null = Invoke-Git add -A
        foreach ($b in $blocked) { $null = Invoke-Git restore --staged -- $b 2>$null }
    } else {
        foreach ($p in $ok) {
            $code = Invoke-Git add -- $p
            if ($code -ne 0) { Write-Host "add uyari: $p exit=$code" -ForegroundColor Yellow }
        }
    }
    Write-Host "Staged (yaklasik): $($ok.Count)"
    $null = Invoke-Git diff --cached --stat
    return $ok.Count
}
function Invoke-Commit {
    if (-not $Onay) {
        Write-Host 'Commit icin -Onay zorunlu.' -ForegroundColor Yellow
        Write-Host 'Ornek: .\scripts\ops\git\commit_push.ps1 -Mod commit -Mesaj "..." -Onay -YeniDal konu'
        exit 9
    }
    if ([string]::IsNullOrWhiteSpace($Mesaj)) {
        Write-Fallback 'mesaj' '-Mesaj gerekli'
        exit 23
    }
    $msgFile = Join-Path $env:TEMP ('kokpitim_commit_msg_{0}.txt' -f [guid]::NewGuid().ToString('N'))
    try {
        $utf8 = New-Object System.Text.UTF8Encoding $false
        [IO.File]::WriteAllText($msgFile, ($Mesaj.TrimEnd() + "`n"), $utf8)
        $code = Invoke-Git commit -F $msgFile
        if ($code -ne 0) {
            Write-Fallback 'commit' "git commit exit=$code (hook reddi olabilir - duzelt, yeni commit)"
            exit 24
        }
    } finally {
        Remove-Item $msgFile -Force -ErrorAction SilentlyContinue
    }
    Write-Host 'Commit OK:' -ForegroundColor Green
    $null = Invoke-Git log -1 --oneline
}
function Invoke-Push {
    Write-Banner 'git push'
    $branch = Get-Branch
    $env:GCM_INTERACTIVE = 'auto'
    $env:GIT_TERMINAL_PROMPT = '1'
    Write-Host "Push: $Uzak HEAD ($branch) ..."
    $code = Invoke-Git push -u $Uzak HEAD
    if ($code -ne 0) {
        Write-Fallback 'push' "git push exit=$code  Dal=$branch  ->  git push -u origin HEAD"
        exit 25
    }
    Write-Host "Push OK: $Uzak / $branch" -ForegroundColor Green
}
if (-not (Test-Path (Join-Path $RepoRoot '.git'))) {
    Write-Fallback 'repo' "$RepoRoot .git yok"
    exit 1
}
Write-Banner "commit_push.ps1 - Mod=$Mod"
switch ($Mod) {
    'durum' { Show-Durum; break }
    'commit' {
        Ensure-Branch
        Show-Durum
        $n = Stage-Files
        if ($n -eq 0) {
            $staged = git -C $RepoRoot diff --cached --name-only
            if (-not $staged) {
                Write-Host 'Commit edilecek degisiklik yok.'
                exit 0
            }
        }
        Invoke-Commit
        if ($Push) { Invoke-Push }
        else { Write-Host 'Push yok (ekle: -Push). Merge/main ayri adim.' -ForegroundColor DarkGray }
        break
    }
}
