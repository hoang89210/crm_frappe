#!/usr/bin/env python3
SIDEBAR = "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue"
ROUTER = "/home/frappe/frappe-bench/apps/crm/frontend/src/router.js"

OLD_LINKS = """  {
    label: 'Kênh',
    icon: WebsiteIcon,
    href: '/kenh',
  },
  {
    label: 'Hàng hóa',
    icon: PackageIcon,
    href: '/app/product-category/view/tree',
  },"""

NEW_LINKS = """  {
    label: 'Kênh',
    icon: WebsiteIcon,
    to: 'Kenh',
  },
  {
    label: 'Hàng hóa',
    icon: PackageIcon,
    to: 'HangHoa',
  },"""

ROUTE_ANCHOR = """  {
    path: '/:invalidpath',
    name: 'Invalid Page',"""

ROUTE_ADD = """  {
    path: '/kenh',
    name: 'Kenh',
    component: () => import('@/pages/Kenh.vue'),
  },
  {
    path: '/hang-hoa',
    name: 'HangHoa',
    component: () => import('@/pages/HangHoa.vue'),
  },
  {
    path: '/:invalidpath',
    name: 'Invalid Page',"""


def main():
    side = open(SIDEBAR, encoding="utf-8").read()
    if "to: 'HangHoa'" in side:
        print("sidebar already routed")
    else:
        if OLD_LINKS not in side:
            raise SystemExit("sidebar anchor missing")
        side = side.replace(OLD_LINKS, NEW_LINKS, 1)
        open(SIDEBAR, "w", encoding="utf-8").write(side)
        print("sidebar patched")

    router = open(ROUTER, encoding="utf-8").read()
    if "name: 'HangHoa'" in router:
        print("router already has HangHoa")
    else:
        if ROUTE_ANCHOR not in router:
            raise SystemExit("router anchor missing")
        router = router.replace(ROUTE_ANCHOR, ROUTE_ADD, 1)
        open(ROUTER, "w", encoding="utf-8").write(router)
        print("router patched")


if __name__ == "__main__":
    main()
