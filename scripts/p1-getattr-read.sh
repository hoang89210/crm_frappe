#!/bin/bash
grep -n "def get_attr" -A 25 /home/frappe/frappe-bench/apps/frappe/frappe/__init__.py | head -35
echo "=== get_module ==="
grep -n "def get_module" -A 15 /home/frappe/frappe-bench/apps/frappe/frappe/__init__.py | head -20
