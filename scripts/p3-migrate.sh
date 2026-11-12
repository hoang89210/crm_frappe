#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== migrate start $(date) ==="
bench --site crm.local migrate
echo "MIGRATE_EXIT:$?"
bench --site crm.local clear-cache
echo "=== migrate done $(date) ==="
ls -la /home/frappe/frappe-bench/apps/pushesale/pushesale/call_bridge/doctype/pushesale_settings/
