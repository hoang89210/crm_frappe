param(
    [string]$TunnelFile = "$PSScriptRoot\..\Test\tunnel-url.txt",
    [string]$User = "Administrator",
    [string]$Pass = "admin"
)

$ErrorActionPreference = "Continue"
$fail = 0
function Report($name, $ok, $detail) {
    if ($ok) { Write-Host "[OK]   $name - $detail" -ForegroundColor Green }
    else { Write-Host "[FAIL] $name - $detail" -ForegroundColor Red; $script:fail++ }
}

Write-Host "=== KIEM TRA SAU REBOOT ===" -ForegroundColor Cyan

$wsl = ((wsl -l --running 2>&1) -join " ") -replace "`0", ""
Report "WSL Ubuntu" ($wsl -match "Ubuntu") $wsl.Trim()

$port = (wsl -u frappe bash -lc "ss -lnt 2>/dev/null | grep -c ':8000 '" 2>&1) -join ""
Report "Bench port 8000" ($port.Trim() -match "^[1-9]") "listeners=$($port.Trim())"

$local = $false
try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/method/ping" -UseBasicParsing -TimeoutSec 15; $local = ($r.StatusCode -eq 200) } catch {}
Report "Bench local HTTP" $local "http://127.0.0.1:8000"

if (-not (Test-Path -LiteralPath $TunnelFile)) {
    Report "Tunnel URL file" $false $TunnelFile
    $url = $null
} else {
    $url = (Get-Content -LiteralPath $TunnelFile -TotalCount 1).Trim()
    Report "Tunnel URL file" ($url -match "^https://") $url
}

if ($url) {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $ok = $false
    for ($i = 1; $i -le 8; $i++) {
        try { $r = Invoke-WebRequest -Uri "$url/login" -UseBasicParsing -TimeoutSec 30; $ok = ($r.StatusCode -eq 200) } catch { $ok = $false }
        if ($ok) { break }
        Write-Host "  ... cho tunnel san sang ($i/8)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 5
    }
    Report "Tunnel /login" $ok $url

    try {
        $body = "usr=$([uri]::EscapeDataString($User))&pwd=$([uri]::EscapeDataString($Pass))"
        $r = Invoke-WebRequest -Uri "$url/api/method/login" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -WebSession $session -UseBasicParsing -TimeoutSec 30
        $ok = ($r.StatusCode -eq 200)
    } catch { $ok = $false }
    Report "Dang nhap" $ok "$User"

    foreach ($p in @("/crm", "/crm/hang-hoa", "/crm/kho", "/crm/kenh")) {
        try { $r = Invoke-WebRequest -Uri "$url$p" -WebSession $session -UseBasicParsing -TimeoutSec 30; $ok = ($r.StatusCode -eq 200) } catch { $ok = $false }
        Report "Route $p" $ok "$($r.StatusCode)"
    }
}

Write-Host ""
if ($fail -eq 0) { Write-Host "KET QUA: TAT CA OK" -ForegroundColor Green; exit 0 }
else { Write-Host "KET QUA: $fail muc FAIL" -ForegroundColor Red; exit 1 }
