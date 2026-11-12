#!/bin/bash
echo "=== sample doctype json ==="
ls /home/frappe/frappe-bench/apps/crm/crm/fcrm/doctype/ | head -30
echo "=== lead source json ==="
cat /home/frappe/frappe-bench/apps/crm/crm/fcrm/doctype/crm_lead_source/crm_lead_source.json 2>/dev/null | head -60
echo "=== call log doctype? ==="
find /home/frappe/frappe-bench/apps/crm/crm -name "*call_log*" | head -5
