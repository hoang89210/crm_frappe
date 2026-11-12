#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
echo "=== fix modules.txt + fixtures ==="
cp /dev/null "$DST/modules.txt"
cp "$SRC/fixtures/custom_field.json" "$DST/fixtures/custom_field.json"
ls -la "$DST/fixtures/"
cat "$DST/modules.txt" | wc -c
echo "=== migrate ==="
cd "$HOME/frappe-bench"
bench --site crm.local migrate 2>&1 | tail -12
echo "MIGRATE_EXIT:$?"
