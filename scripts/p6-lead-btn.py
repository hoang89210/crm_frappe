p = open(
    "/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue",
    encoding="utf-8",
).read()
i = p.find("Gọi SIM")
print(p[i - 700 : i + 400])
print("---API---")
print("open_conversation" in open("/home/frappe/frappe-bench/apps/pushesale/pushesale/api/chatwoot.py", encoding="utf-8").read())
