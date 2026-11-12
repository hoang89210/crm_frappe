#!/bin/bash
cd "$HOME/frappe-bench"
export PATH="$HOME/.local/bin:$PATH"
bench --site crm.local execute pushesale.api.lead.upsert_lead --args "[{'phone': '0901818181', 'first_name': 'Lead Cua Sale1', 'owner': 'sale1@crm.local'}]" > /tmp/upsert.log 2>&1
cat /tmp/upsert.log
