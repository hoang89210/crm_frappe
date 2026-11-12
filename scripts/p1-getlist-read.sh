#!/bin/bash
grep -n "def get_all\|def get_list" /home/frappe/frappe-bench/apps/frappe/frappe/__init__.py
sed -n '/^def get_all/,/^def /p' /home/frappe/frappe-bench/apps/frappe/frappe/__init__.py | head -40
