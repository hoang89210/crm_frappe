#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== drop site start ==="
date
timeout 120 bench drop-site crm.local --db-root-password frappe --force --no-backup 2>&1
echo "EXIT:$?"
date
echo "=== sites now ==="
ls /home/frappe/frappe-bench/sites/
