#!/bin/bash
cd /home/frappe/frappe-bench
bench build --app crm > /tmp/p6-build.log 2>&1
rc=$?
grep -E "built in|DONE|rror" /tmp/p6-build.log | tail -10
echo "BUILD_RC=$rc"
