#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p3_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
export PATH="$HOME/.local/bin:$PATH"
echo "=== copy p3 ==="
mkdir -p "$DST/api" "$DST/tests" "$DST/www" "$DST/call_bridge/doctype/pushesale_settings"
cp "$SRC/hooks.py" "$DST/hooks.py"
cp "$SRC/api/http.py" "$DST/api/http.py"
cp "$SRC/api/settings.py" "$DST/api/settings.py"
cp "$SRC/api/meta.py" "$DST/api/meta.py"
cp "$SRC/api/chatwoot.py" "$DST/api/chatwoot.py"
cp "$SRC/tests/test_settings.py" "$DST/tests/test_settings.py"
cp "$SRC/tests/test_meta.py" "$DST/tests/test_meta.py"
cp "$SRC/www/kenh.html" "$DST/www/kenh.html"
cp "$SRC/call_bridge/__init__.py" "$DST/call_bridge/__init__.py"
cp "$SRC/call_bridge/doctype/__init__.py" "$DST/call_bridge/doctype/__init__.py"
cp "$SRC/call_bridge/doctype/pushesale_settings/__init__.py" "$DST/call_bridge/doctype/pushesale_settings/__init__.py"
cp "$SRC/call_bridge/doctype/pushesale_settings/pushesale_settings.py" "$DST/call_bridge/doctype/pushesale_settings/pushesale_settings.py"
cp "$SRC/call_bridge/doctype/pushesale_settings/pushesale_settings.json" "$DST/call_bridge/doctype/pushesale_settings/pushesale_settings.json"
/home/frappe/frappe-bench/env/bin/python -m py_compile \
  "$DST/hooks.py" "$DST/api/http.py" "$DST/api/settings.py" "$DST/api/meta.py" "$DST/api/chatwoot.py" \
  "$DST/tests/test_settings.py" "$DST/tests/test_meta.py" \
  "$DST/call_bridge/doctype/pushesale_settings/pushesale_settings.py" && echo "compile OK"
echo "=== migrate ==="
cd "$HOME/frappe-bench"
bench --site crm.local migrate 2>&1 | tail -20
echo "MIGRATE_EXIT:$?"
bench --site crm.local clear-cache >/dev/null 2>&1
echo "=== tests ==="
bench --site crm.local run-tests --app pushesale > /tmp/p3t.log 2>&1
tail -20 /tmp/p3t.log
echo "TEST_EXIT:$?"
