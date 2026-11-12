#!/bin/bash
echo "=== PROC ==="
ps aux | grep -E "bench|drop|mysql|git" | grep -v grep || echo "no matching proc"
echo "=== SITES ==="
ls /home/frappe/frappe-bench/sites/
echo "=== CRM BRANCH ==="
cd /home/frappe/frappe-bench/apps/crm && git branch --show-current; git describe --tags 2>&1 || true
echo "=== APPS.TXT ==="
cat /home/frappe/frappe-bench/sites/apps.txt
echo "=== DONE ==="
