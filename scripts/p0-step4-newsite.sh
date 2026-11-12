#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== yarn install crm v1.85.1 ==="
date
cd "$HOME/frappe-bench/apps/crm"
yarn install --check-files 2>&1 | tail -3
echo "YARN_EXIT:$?"
date
cd "$HOME/frappe-bench"
echo "=== new-site crm.local ==="
bench new-site crm.local --db-root-password frappe --admin-password admin 2>&1 | tail -8
echo "SITE_EXIT:$?"
echo "=== STEP4 DONE ==="
