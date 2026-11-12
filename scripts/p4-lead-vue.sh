#!/bin/bash
F=/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue
echo "lines: $(wc -l < $F)"
grep -n -i "call\|telephony\|exotel\|twilio" "$F" | head -40
