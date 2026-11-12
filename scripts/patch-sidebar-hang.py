#!/usr/bin/env python3
PATH = "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue"

ANCHOR = """  {
    label: 'Kênh',
    icon: WebsiteIcon,
    href: '/kenh',
  },"""

ADD = """  {
    label: 'Kênh',
    icon: WebsiteIcon,
    href: '/kenh',
  },
  {
    label: 'Hàng hóa',
    icon: PackageIcon,
    href: '/app/product-category/view/tree',
  },"""

IMPORT_ANCHOR = "import WebsiteIcon from '@/components/Icons/WebsiteIcon.vue'\n"
IMPORT_ADD = (
    "import WebsiteIcon from '@/components/Icons/WebsiteIcon.vue'\n"
    "import PackageIcon from '~icons/lucide/package'\n"
)


def main():
    with open(PATH, encoding="utf-8") as f:
        src = f.read()
    if "label: 'Hàng hóa'" in src:
        print("Hàng hóa already present")
    else:
        if src.count(ANCHOR) != 1:
            raise SystemExit(f"anchor found {src.count(ANCHOR)}x")
        src = src.replace(ANCHOR, ADD)
    if "lucide/package" not in src:
        if src.count(IMPORT_ANCHOR) != 1:
            raise SystemExit("import anchor missing")
        src = src.replace(IMPORT_ANCHOR, IMPORT_ADD)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(src)
    print("patched")


if __name__ == "__main__":
    main()
