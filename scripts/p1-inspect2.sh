#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
bench --site crm.local execute pushesale.inspect_lead_fields.dump_fields 2>&1 | tail -80
echo "EXEC_EXIT:$?"
