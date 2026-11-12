#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/pushesale/tests/test_gates.py" "$DST/tests/test_gates.py"
rm -f "$DST/verify_gates.py"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale 2>&1 | tail -8
echo "TEST_EXIT:$?"
