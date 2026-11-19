import json

import frappe

from pushesale import catalog, stock

DEMO_LEADS = [
	{
		"first_name": "Nguyễn Thu Hà",
		"phone": "0901000001",
		"status": "New",
		"care": "Mới",
		"source": "Facebook",
		"products": [("SON-DO", 1), ("KEM-CN", 2)],
	},
	{
		"first_name": "Trần Minh Anh",
		"phone": "0901000002",
		"status": "Contacted",
		"care": "Đang chăm",
		"source": "Chatwoot",
		"products": [("COMBO-SON", 1)],
	},
	{
		"first_name": "Lê Văn Hùng",
		"phone": "0901000003",
		"status": "Qualified",
		"care": "Cần chăm tiếp",
		"source": "Facebook",
		"products": [("TRA-XANH", 3)],
	},
	{
		"first_name": "Phạm Ngọc Mai",
		"phone": "0901000004",
		"status": "Converted",
		"care": "Chốt",
		"source": "Reference",
		"products": [("BANH-QY", 2), ("SON-NUDE", 1)],
	},
	{
		"first_name": "Đỗ Quang Nam",
		"phone": "0901000005",
		"status": "Nurture",
		"care": "Churn",
		"source": "Facebook",
		"products": [],
	},
]

STOCK_IN = [
	("SON-DO", 50),
	("SON-NUDE", 40),
	("KEM-CN", 30),
	("KEM-AM", 25),
	("TRA-XANH", 100),
	("BANH-QY", 60),
]

DEMO_TAG = "DEMO SEED"


def _delete_doc(doctype, name):
	if name and frappe.db.exists(doctype, name):
		frappe.delete_doc(doctype, name, ignore_permissions=True, force=1)


def reset_demo():
	for name in frappe.get_all(
		"CRM Lead", filters={"lead_name": ["like", "DEMO - %"]}, pluck="name"
	):
		try:
			frappe.delete_doc("CRM Lead", name, ignore_permissions=True, force=1)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "demo reset lead")
	for name in frappe.get_all(
		"Stock Entry", filters={"remarks": DEMO_TAG}, pluck="name"
	):
		doc = frappe.get_doc("Stock Entry", name)
		try:
			if doc.docstatus == 1:
				doc.flags.ignore_permissions = True
				doc.cancel()
			frappe.delete_doc("Stock Entry", name, ignore_permissions=True, force=1)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "demo reset stock entry")
	for name in frappe.get_all(
		"CRM Product", filters={"name": ["like", "TMP-%"]}, pluck="name"
	):
		for row in frappe.get_all(
			"Product Combo Line", filters={"combo": name}, pluck="name"
		):
			_delete_doc("Product Combo Line", row)
		for row in frappe.get_all(
			"Product Combo Line", filters={"item": name}, pluck="name"
		):
			_delete_doc("Product Combo Line", row)
		_delete_doc("CRM Product", name)
	for name in frappe.get_all(
		"Product Category",
		filters={"name": ["in", ["Nhóm test xóa", "Nhóm tạm", "TMP-CAT-A", "TMP-CAT-B"]]},
		pluck="name",
	):
		_delete_doc("Product Category", name)
	for name in frappe.get_all(
		"Warehouse", filters={"name": ["like", "TMP-%"]}, pluck="name"
	):
		_delete_doc("Warehouse", name)
	for name in frappe.get_all(
		"Facebook Page Channel",
		filters={"page_url": ["like", "%demo%"]},
		pluck="name",
	):
		_delete_doc("Facebook Page Channel", name)
	frappe.db.commit()
	print("reset: done")


def _seed_stock():
	for item, qty in STOCK_IN:
		if not frappe.db.exists("CRM Product", item):
			continue
		stock.submit_entry(
			entry_type="Nhập",
			to_warehouse="Kho chính",
			remarks=DEMO_TAG,
			lines=json.dumps([{"item": item, "qty": qty}]),
		)


def _seed_leads():
	meta = frappe.get_meta("CRM Lead")
	for row in DEMO_LEADS:
		lead_name = "DEMO - " + row["first_name"]
		if frappe.db.exists("CRM Lead", {"lead_name": lead_name}):
			continue
		data = {
			"doctype": "CRM Lead",
			"first_name": row["first_name"],
			"lead_name": lead_name,
			"status": row["status"],
			"custom_care_status": row["care"],
			"custom_source_detail": row["source"],
			"products": [
				{
					"product_code": code,
					"product_name": frappe.db.get_value(
						"CRM Product", code, "product_name"
					)
					or code,
					"qty": qty,
					"rate": frappe.db.get_value(
						"CRM Product", code, "standard_rate"
					)
					or 0,
				}
				for code, qty in row["products"]
			],
		}
		for field in ("phone", "mobile_no"):
			if meta.has_field(field):
				data[field] = row["phone"]
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
	frappe.db.commit()


def _seed_fb_page():
	if frappe.db.exists(
		"Facebook Page Channel", {"page_url": "https://facebook.com/demo-page"}
	):
		return
	frappe.get_doc(
		{
			"doctype": "Facebook Page Channel",
			"page_name": "Page Demo (chưa kết nối)",
			"page_id": "000000000000000",
			"page_url": "https://facebook.com/demo-page",
			"sync_enabled": 0,
			"last_result": "Trang demo, chưa có token thật",
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()


def _seed_users():
	try:
		from pushesale.setup_sales_users import create_demo_sales

		create_demo_sales()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "demo seed users")


def seed_demo():
	catalog.seed()
	stock.seed()
	_seed_stock()
	_seed_leads()
	_seed_fb_page()
	frappe.db.commit()
	print(
		"counts",
		frappe.db.count("CRM Product"),
		frappe.db.count("Product Category"),
		frappe.db.count("CRM Lead"),
	)


def run():
	reset_demo()
	print("DEMO_RESET_OK")
