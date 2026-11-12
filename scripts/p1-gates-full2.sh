#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local run-tests --app pushesale --test test_gates > /tmp/gates.log 2>&1
echo "EXIT:$?"
grep -E "^(FAIL|ERROR|ok|Ran|OK|FAILED)" /tmp/gates.log | head -30
echo "=== error headers ==="
grep -B1 -A6 "^ERROR:" /tmp/gates.log | head -60
