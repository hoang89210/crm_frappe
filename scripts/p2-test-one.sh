#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local run-tests --app pushesale --test pushesale.tests.test_chatwoot > /tmp/cw.log 2>&1
grep -E "^(FAIL|ERROR|OK|Ran|FAILED)" /tmp/cw.log | head
sed -n '/FAIL:/,/^====/p' /tmp/cw.log | head -20
