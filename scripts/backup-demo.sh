#!/bin/bash
set -e
export PATH="$HOME/.local/bin:$PATH"
cd /home/frappe/frappe-bench
bench --site crm.local backup --with-files
ts=$(date +%Y%m%d-%H%M%S)
dir="/mnt/c/Users/Dien/Desktop/CRM_Frappe/Test/backups/$ts"
mkdir -p "$dir"
find sites/crm.local/private/backups -maxdepth 1 -type f -mmin -10 -exec cp -t "$dir" {} +
echo "BACKUP_DIR=$dir"
ls -1 "$dir"
