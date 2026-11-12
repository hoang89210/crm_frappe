p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue",
    encoding="utf-8",
).read()
i = p.find("<script")
print(p[i : i + 1200])
