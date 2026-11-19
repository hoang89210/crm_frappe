"""Post-install: create custom roles used by pushesale permissions."""

import frappe


def after_install():
	for role in ("Marketing", "Bridge"):
		if not frappe.db.exists("Role", role):
			doc = frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 0})
			doc.insert(ignore_permissions=True)
