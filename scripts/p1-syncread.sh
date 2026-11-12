#!/bin/bash
grep -n "def sync_for" -A 30 /home/frappe/frappe-bench/apps/frappe/frappe/modules/import_file.py 2>/dev/null || true
echo "=== search sync doctypes ==="
grep -rn "def sync_all\|def sync_for\|get_module_list" /home/frappe/frappe-bench/apps/frappe/frappe/modules/sync.py 2>/dev/null | head
ls /home/frappe/frappe-bench/apps/frappe/frappe/modules/
echo "=== read sync code ==="
sed -n '1,120p' /home/frappe/frappe-bench/apps/frappe/frappe/model/sync.py 2>/dev/null | head -130
