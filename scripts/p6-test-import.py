import base64
from io import BytesIO

import frappe
from openpyxl import Workbook

from pushesale.catalog import import_products


def run():
	frappe.init(site="crm.local", sites_path="/home/frappe/frappe-bench/sites")
	frappe.connect()
	frappe.set_user("Administrator")
	wb = Workbook()
	ws = wb.active
	ws.append(["product_code", "product_name", "category", "uom", "weight_kg", "rate", "short_description"])
	ws.append(["IMP-TEST", "Hang import", "Nhom import", "cai", 0.2, 99000, "test"])
	buf = BytesIO()
	wb.save(buf)
	res = import_products(filedata=base64.b64encode(buf.getvalue()).decode())
	print(res)
	assert res["created"] == 1 or res["updated"] == 1
	assert frappe.db.exists("CRM Product", "IMP-TEST")
	frappe.delete_doc("CRM Product", "IMP-TEST", ignore_permissions=True, force=1)
	if frappe.db.exists("Product Category", "Nhom import"):
		frappe.delete_doc("Product Category", "Nhom import", ignore_permissions=True, force=1)
	frappe.db.commit()
	print("IMPORT_TEST_OK")


if __name__ == "__main__":
	run()
