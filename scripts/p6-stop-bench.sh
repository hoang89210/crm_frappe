#!/bin/bash
pkill -f "bench start" || true
pkill -f "honcho" || true
pkill -f "frappe-bench/env/bin/python" || true
pkill -f "frappe-bench/apps/frappe/frappe" || true
sleep 3
ss -lnt | grep -E ":8000|:9000|:13000|:11000" || echo NO_LISTENERS
pgrep -a redis-server || true
