#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.api.call.register_device --args "['May Sale 1']" > /tmp/reg.log 2>&1
cat /tmp/reg.log
