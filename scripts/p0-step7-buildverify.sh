#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== build crm assets ==="
date
bench build --app crm 2>&1 | tail -5
echo "BUILD_EXIT:$?"
date
echo "=== curl crm again ==="
curl -s -o /dev/null -w "crm HTTP:%{http_code}\n" http://127.0.0.1:8000/crm
curl -s http://127.0.0.1:8000/api/method/frappe.auth.get_logged_user 2>&1 | head -c 200
echo ""
echo "=== check CRM Lead doctype via console ==="
bench --site crm.local console 2>&1 <<'PYEOF' | tail -15
import frappe
frappe.connect()
print("doctype exists:", frappe.db.exists("DocType", "CRM Lead"))
meta = frappe.get_meta("CRM Lead")
print("fields:", len(meta.fields))
print("has mobile_no:", any(f.fieldname=="mobile_no" for f in meta.fields))
print("VERIFIED")
PYEOF
echo "=== VERIFY2 DONE ==="
