#!/bin/bash
cp /mnt/c/Users/Dien/Desktop/CRM_Frappe/temp_code/repro_care.py /home/frappe/frappe-bench/apps/pushesale/pushesale/repro_care.py
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.repro_care.repro 2>&1 | tail -12
