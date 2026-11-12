#!/bin/bash
cat /home/frappe/frappe-bench/apps/crm/crm/permissions/org_hierarchy.py 2>/dev/null || find /home/frappe/frappe-bench/apps/crm/crm/permissions -name "*.py" | head
