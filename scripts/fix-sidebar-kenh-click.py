#!/usr/bin/env python3
PATH = "/home/frappe/frappe-bench/apps/crm/frontend/src/components/Layouts/AppSidebar.vue"
OLD = '@click="(e) => { if (link.href) { window.location.href = link.href; return } selectItem(e, link.key) }"'
NEW = ':onClick="(e) => { if (link.href) { window.location.assign(link.href); return } selectItem(e, link.key) }"'


def main():
    with open(PATH, encoding="utf-8") as f:
        src = f.read()
    if NEW in src:
        print("already fixed")
        return
    n = src.count(OLD)
    if n != 1:
        raise SystemExit(f"old click found {n}x, aborting")
    src = src.replace(OLD, NEW)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(src)
    print("click fixed to :onClick + location.assign")


if __name__ == "__main__":
    main()
