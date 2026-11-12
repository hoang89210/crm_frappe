#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p4_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
cp "$SRC/www/call.html" "$DST/www/call.html"
cp "$SRC/setup_sales_users.py" "$DST/setup_sales_users.py"
echo "pwa + setup copied"
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local run-tests --app pushesale > /tmp/t.log 2>&1
tail -5 /tmp/t.log
