#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
cp "$SRC/pushesale/doctype/call_log/call_log.json" "$DST/call_bridge/doctype/call_log/call_log.json"
cp "$SRC/pushesale/tests/test_lead_upsert.py" "$DST/tests/test_lead_upsert.py"
rm -f "$DST/repro_care.py" "$DST/diag_doctype.py" "$DST/check_doctypes.py" "$DST/inspect_lead_fields.py" "$DST/inspect2.py"
cd "$HOME/frappe-bench"
bench --site crm.local migrate 2>&1 | tail -4
echo "MIGRATE_EXIT:$?"
bench --site crm.local run-tests --app pushesale 2>&1 | tail -8
echo "TEST_EXIT:$?"
