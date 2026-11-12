#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/pushesale/tests/test_debug.py" "$DST/tests/test_debug.py"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale --test pushesale.tests.test_debug > /tmp/dbg.log 2>&1
grep -E "GET_ALL_COUNT|LAST_QUERY" /tmp/dbg.log | head -6
