import os
root = "/home/frappe/frappe-bench/apps/frappe/frappe/public/js"
# find tree route hint
for dirpath, _, files in os.walk("/home/frappe/frappe-bench/apps/frappe/frappe"):
    for name in files:
        if name == "router.js":
            print(os.path.join(dirpath, name))
