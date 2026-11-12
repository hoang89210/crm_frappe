#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
grep -l "Kênh" /home/frappe/frappe-bench/apps/crm/crm/public/frontend/assets/*.js | head -5
echo "---"
cd "$HOME/frappe-bench"
bench --site crm.local clear-cache
echo CACHE_OK
