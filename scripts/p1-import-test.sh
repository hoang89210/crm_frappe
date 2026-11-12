#!/bin/bash
cd "$HOME/frappe-bench"
/home/frappe/frappe-bench/env/bin/python -c "
import sys
sys.path.insert(0, 'apps/pushesale')
sys.path.insert(0, 'apps/frappe')
try:
    import pushesale.verify_gates as m
    print('import OK', hasattr(m, 'verify_gates'))
except Exception as e:
    print('IMPORT FAIL', type(e).__name__, str(e)[:500])
"
file /home/frappe/frappe-bench/apps/pushesale/pushesale/verify_gates.py
head -c 200 /home/frappe/frappe-bench/apps/pushesale/pushesale/verify_gates.py | od -c | head -5
