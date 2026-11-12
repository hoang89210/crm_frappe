#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p3_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
cp "$SRC/hooks.py" "$DST/hooks.py"
cp "$SRC/api/http.py" "$DST/api/http.py"
cp "$SRC/api/settings.py" "$DST/api/settings.py"
cp "$SRC/api/meta.py" "$DST/api/meta.py"
cp "$SRC/api/chatwoot.py" "$DST/api/chatwoot.py"
cp "$SRC/tests/test_settings.py" "$DST/tests/test_settings.py"
cp "$SRC/tests/test_meta.py" "$DST/tests/test_meta.py"
cp "$SRC/www/kenh.html" "$DST/www/kenh.html"
cp "$SRC/call_bridge/doctype/pushesale_settings/pushesale_settings.json" "$DST/call_bridge/doctype/pushesale_settings/pushesale_settings.json"
cp "$SRC/call_bridge/doctype/pushesale_settings/pushesale_settings.py" "$DST/call_bridge/doctype/pushesale_settings/pushesale_settings.py"
echo "copied"
cd "$HOME/frappe-bench"
bench --site crm.local run-tests --app pushesale > /tmp/p3t.log 2>&1
echo "TEST_EXIT:$?"
tail -25 /tmp/p3t.log
