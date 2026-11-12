#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
echo "=== try known-good module ==="
bench --site crm.local execute pushesale.install.after_install 2>&1 | tail -3
echo "=== list installed apps ==="
cat /home/frappe/frappe-bench/sites/apps.txt
