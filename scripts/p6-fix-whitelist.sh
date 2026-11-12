#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
python3 - << 'PY'
from pathlib import Path
pairs = [
    ("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale/catalog.py",
     "/home/frappe/frappe-bench/apps/pushesale/pushesale/catalog.py"),
    ("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale/stock.py",
     "/home/frappe/frappe-bench/apps/pushesale/pushesale/stock.py"),
    ("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/crm-frontend/pages/HangHoa.vue",
     "/home/frappe/frappe-bench/apps/crm/frontend/src/pages/HangHoa.vue"),
]
for src, dst in pairs:
    Path(dst).write_bytes(Path(src).read_bytes().replace(b"\r\n", b"\n"))
    print("copied", dst)
text = Path("/home/frappe/frappe-bench/apps/pushesale/pushesale/catalog.py").read_text()
if "@frappe.whitelist()\ndef delete_product" not in text and "@frappe.whitelist()\r\ndef delete_product" not in text:
    raise SystemExit("whitelist not on delete_product")
if "@frappe.whitelist()\ndef _flag" in text:
    raise SystemExit("whitelist still on _flag")
print("whitelist ok")
PY
cd /home/frappe/frappe-bench
bench --site crm.local clear-cache
bench build --app crm
echo WHITELIST_FIX_DONE
