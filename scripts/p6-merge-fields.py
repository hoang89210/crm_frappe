import json

live = "/home/frappe/frappe-bench/apps/pushesale/pushesale/fixtures/custom_field.json"
sources = [
    "/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale/fixtures/crm_product_fields.json",
    "/mnt/c/Users/Dien/Desktop/CRM_Frappe/p6_code/pushesale/fixtures/facebook_page_lead_fields.json",
]
data = json.load(open(live, encoding="utf-8"))
names = {row.get("name") for row in data}
added = 0
for path in sources:
    for row in json.load(open(path, encoding="utf-8")):
        if row["name"] not in names:
            data.append(row)
            names.add(row["name"])
            added += 1
with open(live, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"added_fields={added} total={len(data)}")
