#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== install crm ==="
date
bench --site crm.local install-app crm 2>&1 | tail -6
echo "CRM_EXIT:$?"
date
echo "=== install pushesale ==="
bench --site crm.local install-app pushesale 2>&1 | tail -6
echo "PUSH_EXIT:$?"
date
echo "=== set default site + configs ==="
bench use crm.local 2>&1 | tail -2
bench --site crm.local set-config FRAPPE_URL "http://crm.local:8000" 2>&1 | tail -1
bench --site crm.local set-config CHATWOOT_WEBHOOK_SECRET "change-me" 2>&1 | tail -1
bench --site crm.local set-config META_VERIFY_TOKEN "verify-me" 2>&1 | tail -1
bench --site crm.local set-config CHATWOOT_URL "" 2>&1 | tail -1
bench --site crm.local set-config CHATWOOT_ACCOUNT_ID "" 2>&1 | tail -1
bench --site crm.local set-config CHATWOOT_API_TOKEN "" 2>&1 | tail -1
bench --site crm.local set-config META_APP_SECRET "" 2>&1 | tail -1
bench --site crm.local set-config META_PAGE_ID "" 2>&1 | tail -1
bench --site crm.local set-config META_PAGE_TOKEN "" 2>&1 | tail -1
echo "=== installed apps ==="
cat "$HOME/frappe-bench/sites/apps.txt"
echo "=== STEP5 DONE ==="
