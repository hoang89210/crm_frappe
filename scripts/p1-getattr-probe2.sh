#!/bin/bash
cd /home/frappe/frappe-bench/sites
/home/frappe/frappe-bench/env/bin/python -c "
import frappe
frappe.init(site='crm.local', sites_path='/home/frappe/frappe-bench/sites')
frappe.connect()
print('installed:', frappe.get_installed_apps())
import traceback
for m in ['pushesale.install.after_install', 'pushesale.manual_iso.manual_check', 'pushesale.verify_gates.verify_gates']:
    try:
        fn = frappe.get_attr(m)
        print(m, '-> OK')
    except Exception as e:
        print(m, '-> FAIL', type(e).__name__, str(e)[:300])
        traceback.print_exc()
" 2>&1 | tail -25
