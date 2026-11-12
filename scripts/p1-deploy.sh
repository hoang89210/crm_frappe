#!/bin/bash
# Deploy Phase 1 code from Windows workspace into WSL bench app, then migrate.
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p1_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
echo "=== copy files ==="
cp "$SRC/phone.py" "$DST/phone.py"
cp "$SRC/permissions.py" "$DST/permissions.py"
cp "$SRC/install.py" "$DST/install.py"
cp "$SRC/hooks.py" "$DST/hooks.py"
cp "$SRC/modules.txt" "$DST/modules.txt"
cp "$SRC/import_leads.py" "$DST/import_leads.py"
cp "$SRC/sample_leads.csv" /home/frappe/frappe-bench/apps/pushesale/sample_leads.csv
mkdir -p "$DST/api" "$DST/tests" "$DST/fixtures"
cp "$SRC/api/__init__.py" "$DST/api/__init__.py"
cp "$SRC/api/lead.py" "$DST/api/lead.py"
cp "$SRC/api/care.py" "$DST/api/care.py"
cp "$SRC/pushesale/tests/__init__.py" "$DST/tests/__init__.py"
cp "$SRC/pushesale/tests/test_phone.py" "$DST/tests/test_phone.py"
cp "$SRC/pushesale/tests/test_lead_upsert.py" "$DST/tests/test_lead_upsert.py"
cp "$SRC/pushesale/fixtures/custom_field.json" "$DST/fixtures/custom_field.json"
mkdir -p "$DST/doctype/call_device" "$DST/doctype/call_job" "$DST/doctype/call_log"
cp "$SRC/pushesale/doctype/call_device/call_device.json" "$DST/doctype/call_device/call_device.json"
cp "$SRC/pushesale/doctype/call_device/call_device.py" "$DST/doctype/call_device/call_device.py"
cp "$SRC/pushesale/doctype/call_job/call_job.json" "$DST/doctype/call_job/call_job.json"
cp "$SRC/pushesale/doctype/call_job/call_job.py" "$DST/doctype/call_job/call_job.py"
cp "$SRC/pushesale/doctype/call_log/call_log.json" "$DST/doctype/call_log/call_log.json"
cp "$SRC/pushesale/doctype/call_log/call_log.py" "$DST/doctype/call_log/call_log.py"
rm -f "$DST/inspect_lead_fields.py" "$DST/inspect2.py"
rm -rf "$DST/__pycache__" "$DST/api/__pycache__" "$DST/tests/__pycache__"
echo "=== tree ==="
find "$DST" -name "*.py" -newer "$DST/hooks.py" | head -20
ls "$DST" "$DST/api" "$DST/tests" "$DST/fixtures" "$DST/doctype"
echo "=== migrate ==="
cd "$HOME/frappe-bench"
bench --site crm.local migrate 2>&1 | tail -15
echo "MIGRATE_EXIT:$?"
