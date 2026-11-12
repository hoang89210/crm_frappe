#!/bin/bash
sed -n '970,1010p' /home/frappe/frappe-bench/apps/frappe/frappe/model/db_query.py
echo "=== build_match_conditions ==="
grep -n "def build_match_conditions" -A 40 /home/frappe/frappe-bench/apps/frappe/frappe/model/db_query.py | head -50
