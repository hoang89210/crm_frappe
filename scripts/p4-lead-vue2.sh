#!/bin/bash
F=/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue
sed -n '100,170p' "$F"
echo "===== composable telephony ====="
cat /home/frappe/frappe-bench/apps/crm/frontend/src/composables/telephony.js 2>/dev/null || ls /home/frappe/frappe-bench/apps/crm/frontend/src/composables/ | head -30
