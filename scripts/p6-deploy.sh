#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
mkdir -p "$DST/call_bridge/doctype/product_category"
cp "$SRC/catalog.py" "$DST/catalog.py"
cp "$SRC/call_bridge/doctype/product_category/__init__.py" "$DST/call_bridge/doctype/product_category/__init__.py"
cp "$SRC/call_bridge/doctype/product_category/product_category.json" "$DST/call_bridge/doctype/product_category/product_category.json"
cp "$SRC/call_bridge/doctype/product_category/product_category.py" "$DST/call_bridge/doctype/product_category/product_category.py"
cp "$SRC/call_bridge/doctype/product_category/product_category.js" "$DST/call_bridge/doctype/product_category/product_category.js"
python3 - << 'PY'
import pathlib
root = pathlib.Path("/home/frappe/frappe-bench/apps/pushesale/pushesale")
for p in [
    root / "catalog.py",
    root / "call_bridge/doctype/product_category/product_category.py",
    root / "call_bridge/doctype/product_category/product_category.js",
    root / "call_bridge/doctype/product_category/product_category.json",
]:
    b = p.read_bytes().replace(b"\r\n", b"\n")
    p.write_bytes(b)
print("lf ok")
PY
python3 /mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-merge-fields.py
cd /home/frappe/frappe-bench
bench --site crm.local migrate
bench --site crm.local clear-cache
bench --site crm.local execute pushesale.catalog.seed
bench --site crm.local execute pushesale.catalog.verify
echo P6_DONE
