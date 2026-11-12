#!/bin/bash
cp /mnt/c/Users/Dien/Desktop/CRM_Frappe/temp_code/verify_gates.py /home/frappe/frappe-bench/apps/pushesale/pushesale/verify_gates.py
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.verify_gates.verify_gates 2>&1 | tail -15
