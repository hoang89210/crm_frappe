#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
python3 -c "p=open('/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/patch-sidebar-hang.py','rb').read().replace(b'\r\n',b'\n'); open('/tmp/patch-sidebar-hang.py','wb').write(p)"
python3 /tmp/patch-sidebar-hang.py
cd /home/frappe/frappe-bench
bench build --app crm
echo BUILD_OK
