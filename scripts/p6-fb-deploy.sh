#!/bin/bash
set -e
python3 - << 'PY'
import shutil
from pathlib import Path

base = Path("/mnt/c/Users/Dien/Desktop/CRM_Frappe")
app = Path("/home/frappe/frappe-bench/apps/pushesale/pushesale")

def copy(src, dst):
    dst = app / dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes((base / src).read_bytes().replace(b"\r\n", b"\n"))

copy("p6_code/pushesale/api/fb_pages.py", "api/fb_pages.py")
copy("p1_code/pushesale/api/lead.py", "api/lead.py")
copy("p3_code/pushesale/api/meta.py", "api/meta.py")
copy("p3_code/pushesale/hooks.py", "hooks.py")

src_dir = base / "p6_code/pushesale/call_bridge/doctype/facebook_page_channel"
dst_dir = app / "call_bridge/doctype/facebook_page_channel"
dst_dir.mkdir(parents=True, exist_ok=True)
for f in src_dir.iterdir():
    if f.is_file():
        (dst_dir / f.name).write_bytes(f.read_bytes().replace(b"\r\n", b"\n"))

crm_page = Path("/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Kenh.vue")
crm_page.write_bytes((base / "p6_code/crm-frontend/pages/Kenh.vue").read_bytes().replace(b"\r\n", b"\n"))
print("copied")
PY
python3 /mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-merge-fields.py
cd /home/frappe/frappe-bench
bench --site crm.local migrate --skip-search-index > /tmp/p6-fb-migrate.log 2>&1 || { tail -30 /tmp/p6-fb-migrate.log; exit 1; }
bench --site crm.local clear-cache
bench build --app crm > /tmp/p6-fb-build.log 2>&1 || { tail -30 /tmp/p6-fb-build.log; exit 1; }
grep -E "built in|DONE" /tmp/p6-fb-build.log | tail -3
echo P6_FB_DONE
