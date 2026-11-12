#!/bin/bash
cd /home/frappe/frappe-bench
nohup bench start > /tmp/bench-start.log 2>&1 &
echo PID:$!
sleep 14
echo '=== log ==='
tail -25 /tmp/bench-start.log
echo '=== ports ==='
ss -lntp 2>/dev/null | grep 8000 || true
ss -lntp 2>/dev/null | grep 9000 || true
