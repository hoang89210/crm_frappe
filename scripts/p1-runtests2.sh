#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/frappe-bench"
bench --site crm.local set-config allow_tests true 2>&1 | tail -1
bench --site crm.local run-tests --app pushesale 2>&1 | tail -25
echo "TEST_EXIT:$?"
