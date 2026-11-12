#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
cp "$SRC/catalog.py" "$DST/catalog.py"
cp "$SRC/stock.py" "$DST/stock.py"
cp "$SRC/call_bridge/doctype/product_category/product_category.json" "$DST/call_bridge/doctype/product_category/product_category.json"
for dt in warehouse item_bin stock_entry stock_entry_item stock_ledger_entry; do
  mkdir -p "$DST/call_bridge/doctype/$dt"
  cp "$SRC/call_bridge/doctype/$dt/"* "$DST/call_bridge/doctype/$dt/"
done
python3 - << 'PY'
from pathlib import Path
root = Path("/home/frappe/frappe-bench/apps/pushesale/pushesale")
pages = Path("/home/frappe/frappe-bench/apps/crm/frontend/src/pages")
src_pages = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/crm-frontend/pages")
for p in root.rglob("*"):
    if p.suffix in {".py", ".json"} and "product_combo" not in str(p):
        if p.is_file() and ("stock" in p.name or "warehouse" in str(p) or "item_bin" in str(p) or p.name == "catalog.py" or p.name == "product_category.json"):
            p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n"))
for name in ("HangHoa.vue", "Kho.vue"):
    data = (src_pages / name).read_bytes().replace(b"\r\n", b"\n")
    (pages / name).write_bytes(data)
    print("page", name)
Path("/tmp/p6-patch-kho.py").write_bytes(Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-patch-kho.py").read_bytes().replace(b"\r\n", b"\n"))
PY
python3 /tmp/p6-patch-kho.py
cd /home/frappe/frappe-bench
bench --site crm.local migrate
bench --site crm.local clear-cache
bench --site crm.local execute pushesale.stock.seed
bench --site crm.local execute pushesale.catalog.seed
bench build --app crm
echo KHO_DONE
