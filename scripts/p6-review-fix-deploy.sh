#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
python3 - << 'PY'
from pathlib import Path
base = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe")
pairs = [
    ("p6_code/pushesale/catalog.py", "apps/pushesale/pushesale/catalog.py"),
    ("p6_code/pushesale/stock.py", "apps/pushesale/pushesale/stock.py"),
    ("p6_code/pushesale/call_bridge/doctype/stock_entry/stock_entry.json",
     "apps/pushesale/pushesale/call_bridge/doctype/stock_entry/stock_entry.json"),
    ("p6_code/crm-frontend/pages/HangHoa.vue", "apps/crm/frontend/src/pages/HangHoa.vue"),
    ("p6_code/crm-frontend/pages/Kho.vue", "apps/crm/frontend/src/pages/Kho.vue"),
]
root = Path("/home/frappe/frappe-bench")
for src, dst in pairs:
    (root / dst).write_bytes((base / src).read_bytes().replace(b"\r\n", b"\n"))
print("copied")
PY
cd /home/frappe/frappe-bench
bench --site crm.local migrate --skip-search-index
bench --site crm.local clear-cache
bench build --app crm
echo P6_REVIEW_FIX_DONE
