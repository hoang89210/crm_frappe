#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p5_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/api/assign.py" "$DST/api/assign.py"
cp "$SRC/tests/test_assign.py" "$DST/tests/test_assign.py"
/home/frappe/frappe-bench/env/bin/python -m py_compile "$DST/api/assign.py" "$DST/tests/test_assign.py" && echo "compile OK"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale > /tmp/t.log 2>&1
tail -5 /tmp/t.log
