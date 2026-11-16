$ErrorActionPreference = "Stop"
$root = "C:\Users\Dien\Desktop\CRM_Frappe"
$src = Join-Path $root "scripts\demo-seed.py"
$dst = "/home/frappe/frappe-bench/apps/pushesale/pushesale/_demo_seed.py"

Write-Host "Deploy demo-seed module..."
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($src))
wsl -u frappe python3 -c "import base64,sys; open(sys.argv[1],'wb').write(base64.b64decode(sys.argv[2]))" $dst $b64
if ($LASTEXITCODE -ne 0) { Write-Host "Copy module failed" -ForegroundColor Red; exit 1 }

Write-Host "Reset + seed du lieu demo..."
wsl -u frappe bash -lc "cd /home/frappe/frappe-bench && bench --site crm.local execute pushesale._demo_seed.run"
if ($LASTEXITCODE -ne 0) { Write-Host "Reset demo failed" -ForegroundColor Red; exit 1 }

wsl -u frappe bash -lc "cd /home/frappe/frappe-bench && bench --site crm.local clear-cache" | Out-Null

Write-Host "DONE: du lieu demo da duoc reset." -ForegroundColor Green
