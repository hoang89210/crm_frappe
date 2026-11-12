#!/usr/bin/env python3
SIDEBAR = "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue"
ROUTER = "/home/frappe/frappe-bench/apps/crm/frontend/src/router.js"

HANG = """  {
    label: 'Hàng hóa',
    icon: PackageIcon,
    to: 'HangHoa',
  },"""

KHO = HANG + """
  {
    label: 'Kho',
    icon: WarehouseIcon,
    to: 'Kho',
  },"""


def main():
    side = open(SIDEBAR, encoding="utf-8").read()
    if "to: 'Kho'" not in side:
        if HANG not in side:
            raise SystemExit("sidebar HangHoa missing")
        side = side.replace(HANG, KHO, 1)
    if "lucide/warehouse" not in side:
        needle = "import PackageIcon from '~icons/lucide/package'\n"
        if needle not in side:
            raise SystemExit("package import missing")
        side = side.replace(
            needle,
            needle + "import WarehouseIcon from '~icons/lucide/warehouse'\n",
            1,
        )
    open(SIDEBAR, "w", encoding="utf-8").write(side)
    print("sidebar kho ok")

    router = open(ROUTER, encoding="utf-8").read()
    if "name: 'Kho'" not in router:
        anchor = "  {\n    path: '/:invalidpath',"
        add = "  {\n    path: '/kho',\n    name: 'Kho',\n    component: () => import('@/pages/Kho.vue'),\n  },\n" + anchor
        if anchor not in router:
            raise SystemExit("router anchor missing")
        router = router.replace(anchor, add, 1)
        open(ROUTER, "w", encoding="utf-8").write(router)
    print("router kho ok")


if __name__ == "__main__":
    main()
