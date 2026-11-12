#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local run-tests --app pushesale --test pushesale.tests.test_debug > /tmp/dbg.log 2>&1
grep -E "IGNORE_PERM_FLAG|HAS_PERM|GET_ALL_COUNT|QUERY_FN|SESSION" /tmp/dbg.log | head -10
