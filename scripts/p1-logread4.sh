#!/bin/bash
grep -E "^(ERROR|FAIL|ok)|test_debug" /tmp/dbg.log | head -10
echo "=== debug traceback ==="
sed -n '/test_debug_roles_and_query/,/^====/p' /tmp/dbg.log | head -30
