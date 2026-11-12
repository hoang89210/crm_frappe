#!/bin/bash
cd "$HOME/frappe-bench"
echo "=== uninstall whatsapp stub ==="
./env/bin/pip uninstall -y whatsapp 2>&1 | tail -2
rm -rf "$HOME/frappe-bench/apps/whatsapp"
echo "=== remove automation_engine stub ==="
rm -rf "$HOME/frappe-bench/apps/frappe/frappe/automation_engine"
echo "=== reset apps.txt ==="
printf 'frappe\ncrm\npushesale\n' > "$HOME/frappe-bench/sites/apps.txt"
cat "$HOME/frappe-bench/sites/apps.txt"
echo "=== STEP2 DONE ==="
