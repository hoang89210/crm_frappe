#!/bin/bash
# Phase 0 cleanup: drop site, remove stubs, pin CRM v1.85.1
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"

echo "=== drop site crm.local ==="
bench drop-site crm.local --db-root-password frappe --force 2>&1 | tail -5 || echo "site may not exist, continuing"

echo "=== uninstall whatsapp stub pkg ==="
./env/bin/pip uninstall -y whatsapp 2>&1 | tail -2 || true
rm -rf "$HOME/frappe-bench/apps/whatsapp"

echo "=== remove automation_engine stub from frappe core ==="
rm -rf "$HOME/frappe-bench/apps/frappe/frappe/automation_engine"

echo "=== reset apps.txt ==="
printf 'frappe\ncrm\npushesale\n' > "$HOME/frappe-bench/sites/apps.txt"
cat "$HOME/frappe-bench/sites/apps.txt"

echo "=== checkout CRM v1.85.1 ==="
cd "$HOME/frappe-bench/apps/crm"
git fetch upstream --tags 2>&1 | tail -3
git checkout v1.85.1 2>&1 | tail -5
git branch --show-current 2>&1 || true
git describe --tags 2>&1 || true

echo "=== CLEANUP DONE ==="
