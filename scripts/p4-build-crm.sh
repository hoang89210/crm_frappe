#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== build crm frontend ==="
bench build --app crm 2>&1 | tail -4
echo "BUILD_EXIT:$?"
grep -c "Gọi bằng SIM" /home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue
grep -c "simCall" /home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue
