#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p4_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/api/call.py" "$DST/api/call.py"
cp "$SRC/tests/test_call.py" "$DST/tests/test_call.py"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale > /tmp/t.log 2>&1
tail -5 /tmp/t.log
