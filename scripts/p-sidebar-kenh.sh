#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
python3 -c "
p=open('/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/patch-sidebar-kenh.py','rb').read().replace(b'\r\n',b'\n')
open('/tmp/patch-sidebar-kenh.py','wb').write(p)
"
python3 /tmp/patch-sidebar-kenh.py
echo "PATCH_EXIT:$?"
grep -n "Kênh\|link.href" /home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue | head -20
echo "=== build crm ==="
cd "$HOME/frappe-bench"
bench build --app crm
echo "BUILD_EXIT:$?"
