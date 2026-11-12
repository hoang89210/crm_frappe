#!/bin/bash
grep -A8 "LAST_QUERY" /tmp/dbg.log | head -12
