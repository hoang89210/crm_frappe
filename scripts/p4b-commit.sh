#!/bin/bash
cd /home/frappe/frappe-bench/apps/pushesale
export PATH="$HOME/.local/bin:$PATH"
git add -A
git -c user.name="dev" -c user.email="dev@example.com" commit -q -m "Sales login device binding, PWA login flow, lead read check on create_job" 2>&1 | tail -2
git log --oneline -6
