$ErrorActionPreference = "Stop"
$root = "C:\Users\Dien\Desktop\CRM_Frappe"
$src = Join-Path $root "scripts\backup-demo.sh"
$dst = "/tmp/backup-demo.sh"

New-Item -ItemType Directory -Force -Path (Join-Path $root "Test\backups") | Out-Null

Write-Host "Backup site crm.local (db + files)..."
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($src))
wsl -u frappe python3 -c "import base64,sys; open(sys.argv[1],'wb').write(base64.b64decode(sys.argv[2]))" $dst $b64
wsl -u frappe bash $dst
if ($LASTEXITCODE -ne 0) { Write-Host "Backup failed" -ForegroundColor Red; exit 1 }
Write-Host "DONE: backup nam trong Test\backups" -ForegroundColor Green
