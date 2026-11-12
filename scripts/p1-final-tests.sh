#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/pushesale/tests/test_gates.py" "$DST/tests/test_gates.py"
cp "$SRC/pushesale/tests/test_lead_upsert.py" "$DST/tests/test_lead_upsert.py"
rm -f "$DST/tests/test_debug.py" "$DST/manual_iso.py"
cp /home/frappe/frappe-bench/apps/pushesale/sample_leads.csv "$DST/sample_leads.csv"
ls "$DST/sample_leads.csv" "$DST/tests/"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale 2>&1 | tail -6
echo "TEST_EXIT:$?"
