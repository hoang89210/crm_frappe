p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue",
    encoding="utf-8",
).read()
i = p.find("label: 'Hàng hóa'")
print("hang", i)
print(p[i - 80 : i + 220] if i >= 0 else "missing")
print("---click---")
j = p.find("link.href")
print(p[j - 80 : j + 180])
