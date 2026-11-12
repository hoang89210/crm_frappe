#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
bench --site crm.local console 2>&1 <<'PYEOF' | grep -v "^In \|^Do you\|^frappe"
import frappe, json
frappe.connect()
meta = frappe.get_meta("CRM Lead")
for f in meta.fields:
    print(f"{f.fieldname}|{f.fieldtype}|{f.label}|{f.options or ''}")
PYEOF
