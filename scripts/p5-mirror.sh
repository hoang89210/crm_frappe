#!/bin/bash
grep -rni "mirror" /home/frappe/frappe-bench/apps/crm/crm --include="*.py" 2>/dev/null | grep -v __pycache__ | head -10
echo "=== owner in todo api ==="
grep -rn "lead_owner\|owner" /home/frappe/frappe-bench/apps/crm/crm/api/todo.py 2>/dev/null | head -20
