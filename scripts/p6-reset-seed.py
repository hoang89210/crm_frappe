import frappe

from pushesale import catalog, stock


def run():
	for code in ("TMP-IP1", "TMP-IP2", "TMP-SINGLE", "TMP-COMBO"):
		if frappe.db.exists("CRM Product", code):
			for row in frappe.get_all("Product Combo Line", filters={"combo": code}, pluck="name"):
				frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
			for row in frappe.get_all("Product Combo Line", filters={"item": code}, pluck="name"):
				frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
			frappe.delete_doc("CRM Product", code, ignore_permissions=True, force=1)
	for cat in ("Nhóm tạm", "TMP-CAT-A", "TMP-CAT-B"):
		if frappe.db.exists("Product Category", cat):
			frappe.delete_doc("Product Category", cat, ignore_permissions=True, force=1)
	for wh in ("TMP-WH-A", "TMP-WH-B"):
		if frappe.db.exists("Warehouse", wh):
			frappe.delete_doc("Warehouse", wh, ignore_permissions=True, force=1)
	frappe.db.commit()
	catalog.seed()
	stock.seed()
	frappe.db.commit()
	print("counts", frappe.db.count("CRM Product"), frappe.db.count("Product Category"))
	print("RESET_SEED_OK")
