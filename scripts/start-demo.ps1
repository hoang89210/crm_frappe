$ErrorActionPreference = "Continue"
$root = "C:\Users\Dien\Desktop\CRM_Frappe\scripts"

Write-Host "=== 1. Bench ==="
& "$root\start-bench-wsl.ps1"
if ($LASTEXITCODE -ne 0) { Write-Host "Bench start failed"; exit 1 }

Write-Host "=== 2. Quick Tunnel ==="
& "$root\start-quick-tunnel.ps1"
if ($LASTEXITCODE -ne 0) { Write-Host "Tunnel start failed"; exit 1 }

$url = Get-Content "C:\Users\Dien\Desktop\CRM_Frappe\Test\tunnel-url.txt" -ErrorAction SilentlyContinue |
    Where-Object { $_ -match "^https://" } |
    Select-Object -First 1
if (-not $url) { Write-Host "No URL file"; exit 1 }
$url = $url.Trim()

Write-Host "=== 3. Test ==="
& "$root\check-after-reboot.ps1"
if ($LASTEXITCODE -ne 0) { Write-Host "Canh bao: co muc FAIL, xem log phia tren" -ForegroundColor Yellow }
Write-Host ""
Write-Host "URL: $url" -ForegroundColor Cyan
Write-Host "Dang nhap: Administrator / admin"
exit 0
