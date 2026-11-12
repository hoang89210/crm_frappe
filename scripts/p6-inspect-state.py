import frappe


def run():
	print("categories", frappe.get_all("Product Category", pluck="name"))
	print("products", frappe.get_all("CRM Product", pluck="name"))
	print("warehouses", frappe.get_all("Warehouse", pluck="name"))
	print("tmp_left", frappe.db.count("CRM Product", {"name": ["like", "TMP-%"]}))
	print("INSPECT_OK")
