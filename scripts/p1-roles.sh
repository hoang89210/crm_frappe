#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.install.after_install 2>&1 | tail -3
bench --site crm.local execute pushesale.check_doctypes.verify 2>&1 | tail -8
