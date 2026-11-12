#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
cd /home/frappe/frappe-bench
bench build --app crm
echo BUILD_OK
