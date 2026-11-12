$ErrorActionPreference = "Continue"
Write-Host "Starting Frappe bench in WSL..."

$inner = "/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/start-bench-inner.py"
wsl -u frappe python3 $inner
if ($LASTEXITCODE -ne 0) {
    Write-Host "bench launcher failed"
    exit 1
}

$ok = $false
for ($i = 0; $i -lt 25; $i++) {
    $code = wsl -u frappe -- curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8000/login
    if ("$code" -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 2
}
if ($ok) {
    Write-Host "Bench OK on http://127.0.0.1:8000 (WSL)"
    exit 0
}
Write-Host "Bench did not respond on 8000"
exit 1

