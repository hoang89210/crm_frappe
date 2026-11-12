#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.inspect2.dump_all 2>&1 | tail -60
