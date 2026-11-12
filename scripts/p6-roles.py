import json

p = "/home/frappe/frappe-bench/apps/pushesale/pushesale/call_bridge/doctype/call_log/call_log.json"
d = json.load(open(p))
print("perms", [x.get("role") for x in d.get("permissions", [])])
print("module", d.get("module"))
