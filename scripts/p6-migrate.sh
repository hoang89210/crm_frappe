#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
cd /home/frappe/frappe-bench
bench --site crm.local migrate
bench --site crm.local clear-cache
bench --site crm.local execute pushesale.catalog.seed
bench --site crm.local execute pushesale.catalog.verify
echo P6_DONE
