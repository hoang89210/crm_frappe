#!/bin/bash
grep -n "permission_conditions\|def execute\b\|def execute_query\|build_conditions()" /home/frappe/frappe-bench/apps/frappe/frappe/model/db_query.py | head
echo "==="
sed -n '390,470p' /home/frappe/frappe-bench/apps/frappe/frappe/model/db_query.py
