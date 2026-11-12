#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/crm-frontend/pages
DST=/home/frappe/frappe-bench/apps/crm/frontend/src/pages
python3 - << 'PY'
from pathlib import Path
src = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/crm-frontend/pages")
dst = Path("/home/frappe/frappe-bench/apps/crm/frontend/src/pages")
for name in ("Kenh.vue", "HangHoa.vue"):
    data = (src / name).read_bytes().replace(b"\r\n", b"\n")
    (dst / name).write_bytes(data)
    print("copied", name)
p = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-patch-crm-menu.py").read_bytes().replace(b"\r\n", b"\n")
Path("/tmp/p6-patch-crm-menu.py").write_bytes(p)
PY
python3 /tmp/p6-patch-crm-menu.py
cd /home/frappe/frappe-bench
bench build --app crm
echo BUILD_OK
