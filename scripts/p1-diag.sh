#!/bin/bash
cp /mnt/c/Users/Dien/Desktop/CRM_Frappe/temp_code/diag_doctype.py /home/frappe/frappe-bench/apps/pushesale/pushesale/diag_doctype.py
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.diag_doctype.diagnose 2>&1 | tail -20
