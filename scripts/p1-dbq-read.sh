#!/bin/bash
grep -n "permission_query_conditions\|ignore_permissions\|add_security_conditions\|def get_permission_query" /home/frappe/frappe-bench/apps/frappe/frappe/model/db_query.py | head -20
