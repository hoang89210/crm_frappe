#!/bin/bash
cp /mnt/c/Users/Dien/Desktop/CRM_Frappe/temp_code/manual_iso.py /home/frappe/frappe-bench/apps/pushesale/pushesale/manual_iso.py
cp /home/frappe/frappe-bench/apps/pushesale/sample_leads.csv /home/frappe/frappe-bench/apps/pushesale/pushesale/sample_leads.csv
echo "csv copied"
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.manual_iso.manual_check 2>&1 | tail -15
