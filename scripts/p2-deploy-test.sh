#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p2_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/api/chatwoot.py" "$DST/api/chatwoot.py"
cp "$SRC/tests/test_chatwoot.py" "$DST/tests/test_chatwoot.py"
/home/frappe/frappe-bench/env/bin/python -m py_compile "$DST/api/chatwoot.py" "$DST/tests/test_chatwoot.py" && echo "compile OK"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale 2>&1 | tail -6
echo "TEST_EXIT:$?"
