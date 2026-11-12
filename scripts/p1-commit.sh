#!/bin/bash
cd /home/frappe/frappe-bench/apps/pushesale
export PATH="$HOME/.local/bin:$PATH"
if [ ! -d .git ]; then git init -q; fi
git add -A
git -c user.name="dev" -c user.email="dev@example.com" commit -q -m "Phase 1: CRM lead care fields, call doctypes, upsert and tests" 2>&1 | tail -2
git log --oneline -3
echo "=== committed ==="
