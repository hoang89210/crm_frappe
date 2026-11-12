#!/bin/bash
cp /mnt/c/Users/Dien/Desktop/CRM_Frappe/temp_code/inspect_lead_fields.py /home/frappe/frappe-bench/apps/pushesale/pushesale/inspect_lead_fields.py
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.inspect_lead_fields.dump_fields 2>&1 | tail -80
