p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue",
    encoding="utf-8",
).read()
for s in ("Gọi SIM", "simCall", "Make a Call", "const doc = computed"):
    print(s, p.find(s))
