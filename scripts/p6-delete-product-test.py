"""Auto test delete product (API level) + leave manual test data.

Run:
  bench --site crm.local execute pushesale._p6_delete_test.run

Log file: /tmp/p6-delete-test-YYYYMMDD-HHMMSS.log
"""

import json
from datetime import datetime

import frappe

from pushesale import catalog

LOG_PATH = f"/tmp/p6-delete-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
RESULTS = []
REQUESTS = 0


def _now():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message):
	line = f"[{_now()}] {message}"
	print(line)
	with open(LOG_PATH, "a", encoding="utf-8") as f:
		f.write(line + "\n")


def call_api(method, payload=None, fn=None):
	global REQUESTS
	REQUESTS += 1
	log(f"POST /api/method/{method}")
	if payload is not None:
		log("Payload: " + json.dumps(payload, ensure_ascii=False, default=str))
	try:
		res = fn()
		log("Response: 200 " + json.dumps(res, ensure_ascii=False, default=str)[:1200])
		return res
	except Exception as exc:
		log("Response: ERROR " + str(exc)[:1200])
		raise


def check(name, fn):
	try:
		fn()
		RESULTS.append((name, True, ""))
		log(f"[PASS] {name}")
	except Exception as exc:
		RESULTS.append((name, False, str(exc)))
		log(f"[FAIL] {name}: {exc}")


def _cleanup():
	for code in ("TMP-DEL-01", "TMP-DEL-02", "TMP-COMBO-01", "TMP-UI-01", "TMP-UI-02", "TMP-UI-COMBO"):
		if not frappe.db.exists("CRM Product", code):
			continue
		for row in frappe.get_all("Product Combo Line", filters={"combo": code}, pluck="name"):
			frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
		for row in frappe.get_all("Product Combo Line", filters={"item": code}, pluck="name"):
			frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
		frappe.delete_doc("CRM Product", code, ignore_permissions=True, force=1)
	if frappe.db.exists("Product Category", "Nhóm test xóa"):
		frappe.delete_doc("Product Category", "Nhóm test xóa", ignore_permissions=True, force=1)
	frappe.db.commit()
	log("Đã dọn dữ liệu test cũ (nếu có).")


def _save_single(code, name):
	old = code if frappe.db.exists("CRM Product", code) else None
	return call_api(
		"pushesale.catalog.save_product",
		{
			"old_code": old,
			"product_code": code,
			"product_name": name,
			"custom_category": "Nhóm test xóa",
			"custom_uom": "cái",
			"custom_weight_kg": 0.1,
			"standard_rate": 1000,
			"custom_is_combo": 0,
			"lines": "[]",
		},
		lambda: catalog.save_product(
			old_code=old,
			product_code=code,
			product_name=name,
			custom_category="Nhóm test xóa",
			custom_uom="cái",
			custom_weight_kg=0.1,
			standard_rate=1000,
			custom_is_combo=0,
			lines="[]",
		),
	)


def _save_combo(code, name, items):
	old = code if frappe.db.exists("CRM Product", code) else None
	lines = json.dumps([{"item": item, "qty": 1} for item in items])
	return call_api(
		"pushesale.catalog.save_product",
		{
			"old_code": old,
			"product_code": code,
			"product_name": name,
			"custom_category": "Nhóm test xóa",
			"custom_is_combo": 1,
			"standard_rate": 1500,
			"lines": lines,
		},
		lambda: catalog.save_product(
			old_code=old,
			product_code=code,
			product_name=name,
			custom_category="Nhóm test xóa",
			custom_is_combo=1,
			standard_rate=1500,
			lines=lines,
		),
	)


def _delete(code, detach=0, confirm=0):
	return call_api(
		"pushesale.catalog.delete_product",
		{"name": code, "detach_combo": detach, "confirm_combo": confirm},
		lambda: catalog.delete_product(code, detach_combo=detach, confirm_combo=confirm),
	)


def _expect_throw(code, detach, confirm, needle, label):
	try:
		_delete(code, detach, confirm)
	except Exception as exc:
		msg = str(exc)
		assert needle.lower() in msg.lower(), f"{label}: expected {needle!r} in {msg!r}"
		return msg
	raise AssertionError(f"{label}: expected throw containing {needle!r}")


def _category_exists():
	return frappe.db.exists("Product Category", "Nhóm test xóa")


def run():
	log("=== START DELETE PRODUCT TEST ===")
	_cleanup()
	if not _category_exists():
		call_api(
			"pushesale.catalog.save_category",
			{"category_name": "Nhóm test xóa", "is_group": 0},
			lambda: catalog.save_category(category_name="Nhóm test xóa", is_group=0),
		)

	# Case 1: delete single not in combo
	def case1():
		_save_single("TMP-DEL-01", "Xóa lẻ")
		_delete("TMP-DEL-01")
		assert not frappe.db.exists("CRM Product", "TMP-DEL-01")
		assert not frappe.db.exists("Product Combo Line", {"item": "TMP-DEL-01"})

	# Case 2/3: single inside combo
	def case2():
		_save_single("TMP-DEL-02", "Xóa trong combo")
		_save_combo("TMP-COMBO-01", "Combo test", ["TMP-DEL-02"])
		msg = _expect_throw("TMP-DEL-02", 0, 0, "combo", "block in combo")
		assert "TMP-COMBO-01" in msg, msg
		assert frappe.db.exists("CRM Product", "TMP-DEL-02")

	def case3():
		_delete("TMP-DEL-02", detach=1)
		assert not frappe.db.exists("CRM Product", "TMP-DEL-02")
		assert not frappe.db.exists("Product Combo Line", {"item": "TMP-DEL-02"})
		assert frappe.db.exists("CRM Product", "TMP-COMBO-01")

	# Case 4: delete combo -> warning then delete
	def case4():
		_save_single("TMP-DEL-01", "Xóa lẻ")
		_save_combo("TMP-COMBO-01", "Combo test", ["TMP-DEL-01"])
		msg = _expect_throw("TMP-COMBO-01", 0, 0, "sản phẩm lẻ", "combo warning")
		assert "1" in msg, msg
		assert frappe.db.exists("CRM Product", "TMP-COMBO-01")
		_delete("TMP-COMBO-01", confirm=1)
		assert not frappe.db.exists("CRM Product", "TMP-COMBO-01")
		assert not frappe.db.exists("Product Combo Line", {"combo": "TMP-COMBO-01"})
		assert frappe.db.exists("CRM Product", "TMP-DEL-01")
		_delete("TMP-DEL-01")
		assert not frappe.db.exists("CRM Product", "TMP-DEL-01")

	# Case 5: reload / get_list clean
	def case5():
		rows = call_api(
			"frappe.client.get_list",
			{"doctype": "CRM Product", "filters": {"name": ["like", "TMP-DEL-%"]}},
			lambda: frappe.get_all("CRM Product", filters={"name": ["like", "TMP-DEL-%"]}, pluck="name"),
		)
		assert rows == [], rows

	check("1. Xóa SP lẻ không trong combo", case1)
	check("2. Xóa SP trong combo bị chặn", case2)
	check("3. Xóa SP trong combo có detach", case3)
	check("4. Xóa Combo: cảnh báo rồi vẫn xóa", case4)
	check("5. Reload: không còn SP test", case5)

	# Leave manual UI test data
	log("=== TẠO DỮ LIỆU TEST THỦ CÔNG (GIỮ LẠI) ===")
	_save_single("TMP-UI-01", "UI xóa lẻ")
	_save_single("TMP-UI-02", "UI xóa trong combo")
	_save_combo("TMP-UI-COMBO", "UI combo", ["TMP-UI-01", "TMP-UI-02"])
	frappe.db.commit()
	log("Manual data: TMP-UI-01 (lẻ), TMP-UI-02 (lẻ), TMP-UI-COMBO (combo chứa cả 2).")

	passed = sum(1 for _, ok, _ in RESULTS if ok)
	log("=== SUMMARY ===")
	log(f"Total requests logged: {REQUESTS}")
	log(f"Test cases: {passed}/{len(RESULTS)} PASSED")
	for name, ok, err in RESULTS:
		log(f"  {'PASS' if ok else 'FAIL'} - {name}" + (f" ({err})" if err else ""))
	log(f"Log file: {LOG_PATH}")
	if passed != len(RESULTS):
		raise AssertionError(f"{passed}/{len(RESULTS)} passed. Xem log {LOG_PATH}")
	print("DELETE_TEST_OK")
