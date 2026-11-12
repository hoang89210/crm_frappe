#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local run-tests --app pushesale --test pushesale.tests.test_assign > /tmp/a.log 2>&1
grep -E "^(FAIL|ERROR|OK|Ran|FAILED)" /tmp/a.log | head
sed -n '/FAIL:/,/^====/p' /tmp/a.log | head -25
