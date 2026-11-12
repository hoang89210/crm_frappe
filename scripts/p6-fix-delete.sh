#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
python3 - << 'PY'
from pathlib import Path
src = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale/catalog.py")
dst = Path("/home/frappe/frappe-bench/apps/pushesale/pushesale/catalog.py")
dst.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
vue_src = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/crm-frontend/pages/HangHoa.vue")
vue_dst = Path("/home/frappe/frappe-bench/apps/crm/frontend/src/pages/HangHoa.vue")
vue_dst.write_bytes(vue_src.read_bytes().replace(b"\r\n", b"\n"))
print("copied")
PY
cd /home/frappe/frappe-bench
bench build --app crm
echo FIX_DELETE_DONE
