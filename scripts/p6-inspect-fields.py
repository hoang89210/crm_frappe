import json

path = "/home/frappe/frappe-bench/apps/pushesale/pushesale/fixtures/custom_field.json"
data = json.load(open(path, encoding="utf-8"))
print("count", len(data))
print("names", [r.get("name") for r in data])
print("first", json.dumps(data[0], ensure_ascii=False)[:300])
