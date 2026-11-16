$ErrorActionPreference = "Continue"
$urlFile = "C:\Users\Dien\Desktop\CRM_Frappe\Test\tunnel-url.txt"

if (-not (Test-Path -LiteralPath $urlFile)) {
    Write-Host "Chua co file URL: $urlFile" -ForegroundColor Red
    exit 1
}

$url = Get-Content -LiteralPath $urlFile -TotalCount 1
$url = "$url".Trim()
if ($url -notmatch "^https://") {
    Write-Host "URL khong hop le: $url" -ForegroundColor Red
    exit 1
}

Write-Host "URL hien tai: $url" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "$url/login" -UseBasicParsing -TimeoutSec 20
    Write-Host "Truy cap /login: $($r.StatusCode) OK" -ForegroundColor Green
} catch {
    Write-Host "Truy cap /login: FAIL - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
exit 0
