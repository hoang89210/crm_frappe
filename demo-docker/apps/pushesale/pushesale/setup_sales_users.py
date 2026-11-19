"""One-off setup: create demo Sales Users. Run once, then delete or keep for staging.

bench --site crm.local execute pushesale.setup_sales_users.create_demo_sales
"""

import frappe

DEMO_SALES = [
	{"email": "sale1@crm.local", "first_name": "Nguyễn Văn A", "password": "Sale1#crm2026"},
	{"email": "sale2@crm.local", "first_name": "Trần Thị B", "password": "Sale2#crm2026"},
	{"email": "sale3@crm.local", "first_name": "Lê Văn C", "password": "Sale3#crm2026"},
]


def create_demo_sales():
	frappe.connect()
	done = []
	for s in DEMO_SALES:
		if frappe.db.exists("User", s["email"]):
			done.append(f"{s['email']} (exists)")
			continue
		u = frappe.get_doc(
			{
				"doctype": "User",
				"email": s["email"],
				"first_name": s["first_name"],
				"roles": [{"role": "Sales User"}],
				"send_welcome_email": 0,
				"new_password": s["password"],
			}
		)
		u.insert(ignore_permissions=True)
		done.append(f"{s['email']} (created)")
	frappe.db.commit()
	return "\n".join(done)
