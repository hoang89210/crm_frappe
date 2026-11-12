p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue",
    encoding="utf-8",
).read()
m = p.find(".map((link)")
print(p[m : m + 450])
