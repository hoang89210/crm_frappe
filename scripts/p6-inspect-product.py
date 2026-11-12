import json

p = "/home/frappe/frappe-bench/apps/crm/crm/fcrm/doctype/crm_product/crm_product.json"
d = json.load(open(p))
print("autoname", d.get("autoname"))
print("naming_rule", d.get("naming_rule"))
for f in d["fields"]:
    print(f.get("fieldname"), f.get("fieldtype"), f.get("reqd"))
