#!/bin/bash
echo "=== crm modules.txt ==="
cat /home/frappe/frappe-bench/apps/crm/crm/modules.txt
echo "=== subpackage dirs ==="
ls -d /home/frappe/frappe-bench/apps/crm/crm/fcrm 2>&1
ls /home/frappe/frappe-bench/apps/crm/crm/fcrm/__init__.py 2>&1
ls -d /home/frappe/frappe-bench/apps/crm/crm/api 2>&1
ls /home/frappe/frappe-bench/apps/crm/crm/api/__init__.py 2>&1 || echo "no crm/api init"
ls /home/frappe/frappe-bench/apps/crm/crm/doctype 2>&1 || echo "no crm/doctype dir"
