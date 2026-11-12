p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue",
    encoding="utf-8",
).read()
k = p.find("v-for=\"link in section.views\"")
print("found", k)
print(p[k - 200 : k + 700])
print("---MAP---")
m = p.find("link.href")
print(p[m - 250 : m + 250] if m >= 0 else "no href map")
