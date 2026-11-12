#!/bin/bash
SRC=/mnt/c/Users/Dien/Desktop/CRM_Frappe/p4_code/pushesale
DST=/home/frappe/frappe-bench/apps/pushesale/pushesale
cp "$SRC/www/call.html" "$DST/www/call.html"
ls -la "$DST/www/"
echo "pwa copied"
