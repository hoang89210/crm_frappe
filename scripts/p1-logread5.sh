#!/bin/bash
tail -20 /tmp/dbg.log
echo "=== grep all prints ==="
grep -E "CLIENT|GET_LIST|LEAD_OWNER|Error|FAIL" /tmp/dbg.log | head -12
