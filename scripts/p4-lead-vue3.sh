#!/bin/bash
F=/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue
sed -n '275,310p' "$F"
echo "############"
grep -n "PhoneIcon\|Email2Icon\|toast" "$F" | head -12
