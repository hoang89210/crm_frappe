#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p4_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/api/call.py" "$DST/api/call.py"
cp "$SRC/tests/test_call.py" "$DST/tests/test_call.py"
/home/frappe/frappe-bench/env/bin/python -m py_compile "$DST/api/call.py" "$DST/tests/test_call.py" && echo "compile OK"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale 2>&1 | tail -6
echo "TEST_EXIT:$?"
