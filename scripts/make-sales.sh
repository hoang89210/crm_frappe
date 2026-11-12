#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p4_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
cp "$SRC/setup_sales_users.py" "$DST/setup_sales_users.py"
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.setup_sales_users.create_demo_sales > /tmp/sales.log 2>&1
cat /tmp/sales.log
