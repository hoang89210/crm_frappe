p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue",
    encoding="utf-8",
).read()
i = p.find("label: 'Leads'")
print(p[i : i + 900])
print("---CLICK---")
j = p.find("SidebarItem")
print(p[j : j + 500])
