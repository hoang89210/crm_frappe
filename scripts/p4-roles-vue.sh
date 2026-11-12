#!/bin/bash
grep -n "isManager\|isSales\|getUser\|hasRole\|role" /home/frappe/frappe-bench/apps/crm/frontend/src/stores/users.js | head -25
echo "=== Lead.vue usersStore usage ==="
grep -n "usersStore\|isManager\|isSales" /home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue | head -10
