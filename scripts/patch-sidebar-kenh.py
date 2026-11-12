#!/usr/bin/env python3
"""Add Kênh item to CRM left sidebar (full-page /kenh, not Vue router)."""

PATH = "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue"

ANCHOR_LEADS = """  {
    label: 'Leads',
    icon: LeadsIcon,
    to: 'Leads',
  },"""

ADD_KENH = """  {
    label: 'Leads',
    icon: LeadsIcon,
    to: 'Leads',
  },
  {
    label: 'Kênh',
    icon: WebsiteIcon,
    href: '/kenh',
  },"""

ANCHOR_MAP = """        .map((link) => ({
          label: link.label,
          icon: link.icon,
          key: link.to,
          to: { name: link.to },
        })),"""

ADD_MAP = """        .map((link) => ({
          label: link.label,
          icon: link.icon,
          key: link.href || link.to,
          to: link.href ? undefined : { name: link.to },
          href: link.href,
        })),"""

ANCHOR_CLICK = """              <SidebarItem
                v-for="link in section.views"
                :key="link.key"
                :to="link.to"
                :label="__(link.label)"
                :active="activeItem === link.key"
                @click="selectItem($event, link.key)"
              >"""

ADD_CLICK = """              <SidebarItem
                v-for="link in section.views"
                :key="link.key"
                :to="link.to"
                :label="__(link.label)"
                :active="activeItem === link.key"
                :onClick="(e) => { if (link.href) { window.location.assign(link.href); return } selectItem(e, link.key) }"
              >"""


def main():
    with open(PATH, encoding="utf-8") as f:
        src = f.read()
    with open("/tmp/AppSidebar.vue.bak", "w", encoding="utf-8") as f:
        f.write(src)

    for name, anchor in (
        ("leads", ANCHOR_LEADS),
        ("map", ANCHOR_MAP),
        ("click", ANCHOR_CLICK),
    ):
        if src.count(anchor) != 1:
            raise SystemExit(f"anchor {name!r} found {src.count(anchor)}x, aborting")

    if "label: 'Kênh'" in src:
        print("Kênh item already present, skipping leads insert")
    else:
        src = src.replace(ANCHOR_LEADS, ADD_KENH)

    if "link.href || link.to" in src:
        print("map already patched, skipping")
    else:
        src = src.replace(ANCHOR_MAP, ADD_MAP)

    if "if (link.href)" in src:
        print("click already patched, skipping")
    else:
        src = src.replace(ANCHOR_CLICK, ADD_CLICK)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(src)
    print("AppSidebar.vue patched OK")


if __name__ == "__main__":
    main()
