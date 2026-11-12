#!/bin/bash
cd "$HOME/frappe-bench/apps/crm"
echo "=== fetch single tag v1.85.1 ==="
date
timeout 120 git fetch upstream tag v1.85.1 2>&1
echo "FETCH_EXIT:$?"
date
echo "=== checkout ==="
git checkout v1.85.1 2>&1
echo "=== verify ==="
git describe --tags 2>&1
git log -1 --oneline 2>&1
grep -n "required_apps\|automation_engine" crm/hooks.py || echo "hooks clean: no required_apps/automation_engine"
echo "=== STEP3 DONE ==="
