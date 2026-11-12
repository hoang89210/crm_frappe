#!/bin/bash
cd /home/frappe/frappe-bench/apps/pushesale
export PATH="$HOME/.local/bin:$PATH"
git add -A
git -c user.name="dev" -c user.email="dev@example.com" commit -q -m "Manual lead reassignment API with ownership transfer and tests" 2>&1 | tail -2
git log --oneline -6
