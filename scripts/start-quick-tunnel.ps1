$ErrorActionPreference = "Continue"
Write-Host "Starting Quick Tunnel inside WSL..."
wsl -u frappe python3 /mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/start-quick-tunnel-inner.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tunnel start failed. Log:"
    wsl -u frappe tail -30 /tmp/cloudflared-quick.log
    exit 1
}
$urlFile = "C:\Users\Dien\Desktop\CRM_Frappe\Test\tunnel-url.txt"
if (Test-Path $urlFile) {
    Write-Host "URL file: $(Get-Content $urlFile)"
}
exit 0
