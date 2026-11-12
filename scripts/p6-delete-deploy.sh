#!/bin/bash
set -e
python3 - << 'PY'
from pathlib import Path
base = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe")
root = Path("/home/frappe/frappe-bench")

def cp(src, dst):
    (root / dst).write_bytes((base / src).read_bytes().replace(b"\r\n", b"\n"))

cp("p6_code/pushesale/catalog.py", "apps/pushesale/pushesale/catalog.py")
cp("p6_code/crm-frontend/pages/HangHoa.vue", "apps/crm/frontend/src/pages/HangHoa.vue")
cp("scripts/p6-delete-product-test.py", "apps/pushesale/pushesale/_p6_delete_test.py")
print("copied")
PY
cd /home/frappe/frappe-bench
bench --site crm.local clear-cache
bench build --app crm > /tmp/p6-del-build.log 2>&1 || { tail -30 /tmp/p6-del-build.log; exit 1; }
grep -E "built in|DONE" /tmp/p6-del-build.log | tail -2
echo P6_DELETE_DEPLOY_DONE
