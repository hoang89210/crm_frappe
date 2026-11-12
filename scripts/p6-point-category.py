path = "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue"
src = open(path, encoding="utf-8").read()
old = "href: '/app/crm-product',"
new = "href: '/app/product-category/view/tree',"
if old not in src:
    raise SystemExit("href not found")
src = src.replace(old, new, 1)
open(path, "w", encoding="utf-8").write(src)
print("updated")
