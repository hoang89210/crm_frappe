#!/bin/bash
cd "$HOME/frappe-bench"
/home/frappe/frappe-bench/env/bin/python -c "
import frappe
frappe.init(site='crm.local')
frappe.connect()
print('installed:', frappe.get_installed_apps())
for m in ['pushesale.install.after_install', 'pushesale.manual_iso.manual_check', 'pushesale.verify_gates.verify_gates']:
    try:
        fn = frappe.get_attr(m)
        print(m, '-> OK', fn)
    except Exception as e:
        print(m, '-> FAIL', type(e).__name__, str(e)[:300])
" 2>&1 | tail -8
