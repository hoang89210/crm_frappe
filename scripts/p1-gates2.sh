#!/bin/bash
ls -la /home/frappe/frappe-bench/apps/pushesale/pushesale/verify_gates.py
/home/frappe/frappe-bench/env/bin/python -m py_compile /home/frappe/frappe-bench/apps/pushesale/pushesale/verify_gates.py && echo "syntax OK"
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.verify_gates.verify_gates 2>&1 | tail -15
