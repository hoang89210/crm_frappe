#!/bin/bash
# Restructure: pushesale/pushesale/doctype -> pushesale/pushesale/call_bridge/doctype
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
echo "=== restructure ==="
mkdir -p "$DST/call_bridge"
cp "$SRC/call_bridge/__init__.py" "$DST/call_bridge/__init__.py"
cp "$SRC/modules.txt" "$DST/modules.txt"
mkdir -p "$DST/call_bridge/doctype"
rm -rf "$DST/call_bridge/doctype"
cp -r "$SRC/pushesale/doctype" "$DST/call_bridge/doctype"
rm -rf "$DST/doctype"
echo "=== tree ==="
find "$DST/call_bridge" -type f | head -12
cat "$DST/modules.txt"
echo "=== migrate ==="
cd "$HOME/frappe-bench"
bench --site crm.local migrate 2>&1 | tail -6
echo "MIGRATE_EXIT:$?"
