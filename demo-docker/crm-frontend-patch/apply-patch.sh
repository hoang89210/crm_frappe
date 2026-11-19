#!/bin/bash
set -e
CRM_FE="/home/frappe/frappe-bench/apps/crm/frontend/src"
PATCH="/tmp/crm-frontend-patch"

echo "Patching CRM frontend (HangHoa / Kho / Kenh)..."
cp -f "$PATCH/pages/"*.vue "$CRM_FE/pages/"
cp -f "$PATCH/router.js" "$CRM_FE/router.js"
cp -f "$PATCH/AppSidebar.vue" "$CRM_FE/components/Layouts/AppSidebar.vue"
echo "CRM frontend patch applied"
