#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
echo "=== kill old bench ==="
pkill -f "bench start" || true
sleep 2
echo "=== start bench background ==="
nohup bench start > /tmp/bench-start.log 2>&1 &
echo "bench pid: $!"
sleep 15
echo "=== bench log tail ==="
tail -30 /tmp/bench-start.log
echo "=== curl login page ==="
curl -s -o /dev/null -w "login page HTTP:%{http_code}\n" http://127.0.0.1:8000/login
echo "=== curl crm page ==="
curl -s -o /dev/null -w "crm page HTTP:%{http_code}\n" http://127.0.0.1:8000/crm
echo "=== VERIFY DONE ==="
