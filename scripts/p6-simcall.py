p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue",
    encoding="utf-8",
).read()
i = p.find("async function simCall")
print(p[i : i + 900])
print("---import call---")
print("import { call" in p or "call }" in p[:2500])
print(p[p.find("<script"): p.find("<script")+400])
