#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
mkdir -p "$DST/call_bridge/doctype/product_combo_line"
cp "$SRC/catalog.py" "$DST/catalog.py"
cp "$SRC/call_bridge/doctype/product_combo_line/__init__.py" "$DST/call_bridge/doctype/product_combo_line/__init__.py"
cp "$SRC/call_bridge/doctype/product_combo_line/product_combo_line.py" "$DST/call_bridge/doctype/product_combo_line/product_combo_line.py"
cp "$SRC/call_bridge/doctype/product_combo_line/product_combo_line.json" "$DST/call_bridge/doctype/product_combo_line/product_combo_line.json"
python3 - << 'PY'
from pathlib import Path
root = Path("/home/frappe/frappe-bench/apps/pushesale/pushesale")
for p in [
    root / "catalog.py",
    root / "call_bridge/doctype/product_combo_line/product_combo_line.py",
    root / "call_bridge/doctype/product_combo_line/product_combo_line.json",
]:
    p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n"))
src = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/crm-frontend/pages/HangHoa.vue")
dst = Path("/home/frappe/frappe-bench/apps/crm/frontend/src/pages/HangHoa.vue")
dst.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
print("copied")
PY
python3 /mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-merge-fields.py
cd /home/frappe/frappe-bench
bench --site crm.local migrate
bench --site crm.local clear-cache
bench --site crm.local execute pushesale.catalog.seed
bench --site crm.local execute pushesale.catalog.verify
bench build --app crm
echo COMBO_DONE
