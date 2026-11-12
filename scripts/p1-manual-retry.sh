#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
ls -la /home/frappe/frappe-bench/apps/pushesale/pushesale/manual_iso.py
bench --site crm.local execute pushesale.manual_iso.manual_check 2>&1 | tail -15
