#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
python3 -c "
p=open('/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/fix-sidebar-kenh-click.py','rb').read().replace(b'\r\n',b'\n')
open('/tmp/fix-sidebar-kenh-click.py','wb').write(p)
"
python3 /tmp/fix-sidebar-kenh-click.py
grep -n "onClick\|location.assign" /home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue | head
echo "=== build ==="
cd "$HOME/frappe-bench"
bench build --app crm
echo BUILD_EXIT:$?
bench --site crm.local clear-cache
echo CACHE_OK
