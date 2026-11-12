#!/bin/bash
grep -n "def get_doc" -A 40 /home/frappe/frappe-bench/apps/frappe/frappe/__init__.py | head -60
echo "=== check_permission in document ==="
grep -n "def check_permission" -A 25 /home/frappe/frappe-bench/apps/frappe/frappe/model/document.py | head -30
