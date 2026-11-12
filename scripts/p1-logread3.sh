#!/bin/bash
grep -E "HOOK_CALLED|GET_ALL_COUNT|Error|assert" /tmp/dbg.log | head -10
