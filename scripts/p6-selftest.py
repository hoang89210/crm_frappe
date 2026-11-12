import base64
from io import BytesIO

import frappe
from openpyxl import Workbook

from pushesale import catalog, stock


def _xlsx(rows):
	wb = Workbook()
	ws = wb.active
	ws.append(rows[0])
	for row in rows[1:]:
		ws.append(row)
	buf = BytesIO()
	wb.save(buf)
	return base64.b64encode(buf.getvalue()).decode()


def _expect_throw(fn, needle):
	try:
		fn()
	except Exception as exc:
		msg = str(exc)
		assert needle.lower() in msg.lower(), f"expected {needle!r} in {msg!r}"
		return
	raise AssertionError(f"expected throw containing {needle!r}")


def run():
	log = []

	# 1) import with Vietnamese headers + upsert + combo skip
	data = _xlsx(
		[
			["Mã", "Tên", "Danh mục", "ĐVT", "Kg", "Giá", "Mô tả"],
			["TMP-IP1", "Temp import 1", "Nhóm tạm", "cái", 0.1, 1000, "a"],
			["TMP-IP2", "Temp import 2", "Nhóm tạm", "cái", 0.2, 2000, "b"],
			["COMBO-SON", "Combo son", "Son môi", "bộ", 0.1, 123, "x"],
		]
	)
	res = catalog.import_products(filedata=data)
	log.append(("import1", res))
	assert res["created"] == 2, res
	assert res["skipped"] == 1, res
	assert any("combo" in e["message"].lower() for e in res["errors"]), res
	assert frappe.db.exists("Product Category", "Nhóm tạm")
	assert int(frappe.db.get_value("CRM Product", "COMBO-SON", "custom_is_combo")) == 1

	res2 = catalog.import_products(filedata=data)
	log.append(("import2", res2))
	assert res2["updated"] == 2, res2
	assert float(frappe.db.get_value("CRM Product", "TMP-IP1", "standard_rate")) == 1000

	# 2) delete_product: block when in combo, allow with detach
	catalog.save_product(
		old_code=None,
		product_code="TMP-SINGLE",
		product_name="Temp single",
		custom_is_combo=0,
		lines="[]",
	)
	catalog.save_product(
		old_code=None,
		product_code="TMP-COMBO",
		product_name="Temp combo",
		custom_is_combo=1,
		standard_rate=100,
		lines='[{"item": "TMP-SINGLE", "qty": 2}]',
	)
	_expect_throw(
		lambda: catalog.delete_product("TMP-SINGLE"),
		"combo",
	)
	catalog.delete_product("TMP-SINGLE", detach_combo=1)
	assert not frappe.db.exists("CRM Product", "TMP-SINGLE")
	assert not frappe.db.exists("Product Combo Line", {"item": "TMP-SINGLE"})
	catalog.delete_product("TMP-COMBO", detach_combo=1)

	# 3) category cycle guard
	catalog.save_category(category_name="TMP-CAT-A", is_group=1)
	catalog.save_category(category_name="TMP-CAT-B", parent="TMP-CAT-A", is_group=0)
	_expect_throw(
		lambda: catalog.save_category(old_name="TMP-CAT-A", category_name="TMP-CAT-A", parent="TMP-CAT-B", is_group=1),
		"con",
	)
	catalog.delete_category("TMP-CAT-B")
	catalog.delete_category("TMP-CAT-A")

	# 4) warehouse cycle guard + ledger delete guard
	stock.save_warehouse(warehouse_name="TMP-WH-A", is_group=1)
	stock.save_warehouse(warehouse_name="TMP-WH-B", parent="TMP-WH-A", is_group=0)
	_expect_throw(
		lambda: stock.save_warehouse(old_name="TMP-WH-A", warehouse_name="TMP-WH-A", parent="TMP-WH-B", is_group=1),
		"con",
	)

	# 5) stock nhập/xuất/cancel
	before = stock.bin_qty("SON-DO", "Kho chính")
	e1 = stock.submit_entry(entry_type="Nhập", to_warehouse="Kho chính", lines='[{"item":"SON-DO","qty":5}]')
	assert stock.bin_qty("SON-DO", "Kho chính") == before + 5
	e2 = stock.submit_entry(entry_type="Xuất", from_warehouse="Kho chính", lines='[{"item":"SON-DO","qty":2}]')
	assert stock.bin_qty("SON-DO", "Kho chính") == before + 3
	stock.cancel_entry(e2["name"])
	assert stock.bin_qty("SON-DO", "Kho chính") == before + 5
	stock.cancel_entry(e1["name"])
	assert stock.bin_qty("SON-DO", "Kho chính") == before
	log.append(("stock", "ok"))

	# 6) sell combo deducts components
	c1 = stock.bin_qty("SON-DO", "Kho chính")
	c2 = stock.bin_qty("SON-NUDE", "Kho chính")
	if c1 >= 1 and c2 >= 1:
		e3 = stock.submit_entry(entry_type="Xuất", from_warehouse="Kho chính", lines='[{"item":"COMBO-SON","qty":1}]')
		assert stock.bin_qty("SON-DO", "Kho chính") == c1 - 1
		assert stock.bin_qty("SON-NUDE", "Kho chính") == c2 - 1
		stock.cancel_entry(e3["name"])
		assert stock.bin_qty("SON-DO", "Kho chính") == c1
		log.append(("combo_sell", "ok"))

	# 7) cancel permission for Sales User
	frappe.set_user("sale1@crm.local")
	e4 = stock.submit_entry(entry_type="Nhập", to_warehouse="Kho chính", lines='[{"item":"TMP-IP1","qty":1}]')
	stock.cancel_entry(e4["name"])
	frappe.set_user("Administrator")
	assert stock.bin_qty("TMP-IP1", "Kho chính") == 0
	log.append(("sales_cancel", "ok"))

	# cleanup
	stock.delete_warehouse("TMP-WH-B")
	stock.delete_warehouse("TMP-WH-A")
	catalog.delete_product("TMP-IP1", detach_combo=1)
	catalog.delete_product("TMP-IP2", detach_combo=1)
	if frappe.db.exists("Product Category", "Nhóm tạm"):
		catalog.delete_category("Nhóm tạm")
	frappe.db.commit()
	print("SELFTEST_LOG", log)
	print("SELFTEST_OK")
