#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local run-tests --app pushesale --test test_gates 2>&1 | tail -60
