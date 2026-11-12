Start-Sleep -Seconds 25
wsl -u frappe echo wsl-ready | Out-Null
& "C:\Users\Dien\Desktop\CRM_Frappe\scripts\start-demo.ps1"
