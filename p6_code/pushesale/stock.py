import frappe


def _text(value):
	if value is None or isinstance(value, (dict, list)):
		return ""
	return str(value).strip()


def _flag(value):
	if isinstance(value, bool):
		return int(value)
	if isinstance(value, (int, float)) and not isinstance(value, bool):
		return 1 if int(value) else 0
	return 1 if _text(value).lower() in ("1", "true", "yes") else 0


def _num(value, default=0):
	if isinstance(value, (dict, list)):
		return float(default)
	try:
		return float(value if value not in (None, "") else default)
	except (TypeError, ValueError):
		return float(default)


def _rows(raw):
	if isinstance(raw, list):
		return raw
	if isinstance(raw, dict):
		frappe.throw("Dòng phiếu không hợp lệ")
	try:
		rows = frappe.parse_json(raw or "[]")
	except Exception:
		frappe.throw("Dòng phiếu không hợp lệ")
	if not isinstance(rows, list):
		frappe.throw("Dòng phiếu không hợp lệ")
	return rows


def _is_combo(item):
	return int(frappe.db.get_value("CRM Product", item, "custom_is_combo") or 0)


def _is_group_wh(name):
	return int(frappe.db.get_value("Warehouse", name, "is_group") or 0)


def _descendants_wh(name):
	out = []
	queue = [name]
	while queue:
		parent = queue.pop(0)
		for child in frappe.get_all("Warehouse", filters={"parent_warehouse": parent}, pluck="name"):
			if child in out:
				continue
			out.append(child)
			queue.append(child)
	return out


def explode(item, qty):
	if not _is_combo(item):
		return [(item, qty)]
	lines = frappe.get_all("Product Combo Line", filters={"combo": item}, fields=["item", "qty"])
	if not lines:
		frappe.throw(f"Combo {item} chưa có sản phẩm lẻ")
	return [(row.item, _num(row.qty) * qty) for row in lines]


def movements(doc):
	rows = []
	kind = doc.entry_type
	for line in doc.items:
		item = line.item
		qty = _num(line.qty)
		if qty <= 0:
			frappe.throw("Số lượng phải lớn hơn 0")
		if kind == "Nhập":
			if not doc.to_warehouse:
				frappe.throw("Chọn kho nhập")
			if _is_group_wh(doc.to_warehouse):
				frappe.throw("Không nhập vào kho nhóm")
			if _is_combo(item):
				frappe.throw("Không nhập tồn cho combo. Nhập từng sản phẩm lẻ.")
			rows.append((item, doc.to_warehouse, qty))
		elif kind == "Xuất":
			if not doc.from_warehouse:
				frappe.throw("Chọn kho xuất")
			if _is_group_wh(doc.from_warehouse):
				frappe.throw("Không xuất từ kho nhóm")
			for part, part_qty in explode(item, qty):
				rows.append((part, doc.from_warehouse, -part_qty))
		elif kind == "Điều chuyển":
			if not doc.from_warehouse or not doc.to_warehouse:
				frappe.throw("Chọn kho nguồn và kho đích")
			if doc.from_warehouse == doc.to_warehouse:
				frappe.throw("Hai kho phải khác nhau")
			if _is_combo(item):
				frappe.throw("Điều chuyển chỉ sản phẩm lẻ")
			rows.append((item, doc.from_warehouse, -qty))
			rows.append((item, doc.to_warehouse, qty))
		else:
			frappe.throw("Loại phiếu không hợp lệ")
	return rows


def bin_qty(item, warehouse):
	qty = frappe.db.get_value("Item Bin", {"item": item, "warehouse": warehouse}, "qty")
	return _num(qty)


def add_bin(item, warehouse, delta, voucher=None):
	current = bin_qty(item, warehouse)
	new_qty = current + delta
	if new_qty < -0.0001:
		frappe.throw(f"Không đủ tồn {item} tại {warehouse}: còn {current}, cần {abs(delta)}")
	name = frappe.db.get_value("Item Bin", {"item": item, "warehouse": warehouse}, "name")
	if name:
		doc = frappe.get_doc("Item Bin", name)
		doc.qty = new_qty
		doc.save(ignore_permissions=True)
	else:
		frappe.get_doc(
			{
				"doctype": "Item Bin",
				"item": item,
				"warehouse": warehouse,
				"qty": new_qty,
			}
		).insert(ignore_permissions=True)
	frappe.get_doc(
		{
			"doctype": "Stock Ledger Entry",
			"stock_entry": voucher,
			"item": item,
			"warehouse": warehouse,
			"qty_change": delta,
			"qty_after": new_qty,
		}
	).insert(ignore_permissions=True)
	return new_qty


def apply_entry(doc, sign):
	for item, warehouse, delta in movements(doc):
		add_bin(item, warehouse, delta * sign, doc.name)


def combo_available(combo, warehouse=None):
	lines = frappe.get_all("Product Combo Line", filters={"combo": combo}, fields=["item", "qty"])
	if not lines:
		return 0
	caps = []
	for line in lines:
		need = _num(line.qty) or 1
		if warehouse:
			have = bin_qty(line.item, warehouse)
		else:
			have = _num(
				frappe.db.sql(
					"select sum(qty) from `tabItem Bin` where item=%s",
					line.item,
				)[0][0]
			)
		caps.append(int(have // need))
	return min(caps) if caps else 0


@frappe.whitelist()
def balances(warehouse=None):
	warehouse = _text(warehouse) or None
	filters = {"warehouse": warehouse} if warehouse else None
	bins = frappe.get_all(
		"Item Bin",
		filters=filters,
		fields=["item", "warehouse", "qty"],
		limit_page_length=500,
	)
	totals = {}
	for row in bins:
		totals[row.item] = totals.get(row.item, 0) + _num(row.qty)
	combos = frappe.get_all("CRM Product", filters={"custom_is_combo": 1}, pluck="name")
	available = {name: combo_available(name, warehouse) for name in combos}
	return {"bins": bins, "totals": totals, "combo_available": available}


@frappe.whitelist()
def save_warehouse(old_name=None, warehouse_name=None, parent=None, is_group=0):
	warehouse_name = _text(warehouse_name)
	old_name = _text(old_name) or None
	parent = _text(parent) or None
	if not warehouse_name:
		frappe.throw("Nhập tên kho")
	if parent and parent in (warehouse_name, old_name):
		frappe.throw("Không chọn chính nó làm cha")
	if parent and old_name and frappe.db.exists("Warehouse", old_name):
		if parent in _descendants_wh(old_name):
			frappe.throw("Không chọn kho con làm cha")
	is_group = _flag(is_group)
	if old_name and frappe.db.exists("Warehouse", old_name):
		doc = frappe.get_doc("Warehouse", old_name)
		doc.is_group = is_group
		doc.parent_warehouse = parent
		doc.save(ignore_permissions=True)
		if warehouse_name != old_name:
			frappe.rename_doc("Warehouse", old_name, warehouse_name, force=True)
		frappe.db.commit()
		return {"name": warehouse_name}
	if frappe.db.exists("Warehouse", warehouse_name):
		frappe.throw("Kho đã tồn tại")
	doc = frappe.get_doc(
		{
			"doctype": "Warehouse",
			"warehouse_name": warehouse_name,
			"parent_warehouse": parent,
			"is_group": is_group,
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist()
def delete_warehouse(name):
	name = _text(name)
	if not name or not frappe.db.exists("Warehouse", name):
		frappe.throw("Không thấy kho")
	if frappe.db.exists("Warehouse", {"parent_warehouse": name}):
		frappe.throw("Còn kho con, không xóa được")
	if frappe.db.exists("Item Bin", {"warehouse": name, "qty": [">", 0]}):
		frappe.throw("Kho còn tồn, không xóa được")
	if frappe.db.exists("Stock Ledger Entry", {"warehouse": name}):
		frappe.throw("Kho đã có lịch sử nhập xuất, không xóa được")
	frappe.delete_doc("Warehouse", name, ignore_permissions=True, force=1)
	frappe.db.commit()
	return {"ok": 1}


@frappe.whitelist()
def submit_entry(entry_type, from_warehouse=None, to_warehouse=None, remarks=None, lines=None):
	entry_type = _text(entry_type)
	if entry_type not in ("Nhập", "Xuất", "Điều chuyển"):
		frappe.throw("Loại phiếu không hợp lệ")
	rows = _rows(lines)
	if not rows:
		frappe.throw("Thêm ít nhất 1 dòng")
	doc = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"entry_type": entry_type,
			"from_warehouse": _text(from_warehouse) or None,
			"to_warehouse": _text(to_warehouse) or None,
			"remarks": _text(remarks),
			"items": [
				{"item": _text(r.get("item")), "qty": _num(r.get("qty"))}
				for r in rows
				if isinstance(r, dict) and _text(r.get("item"))
			],
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist()
def cancel_entry(name):
	name = _text(name)
	if not name or not frappe.db.exists("Stock Entry", name):
		frappe.throw("Không thấy phiếu")
	doc = frappe.get_doc("Stock Entry", name)
	if doc.docstatus != 1:
		frappe.throw("Chỉ hủy phiếu đã ghi sổ")
	doc.flags.ignore_permissions = True
	doc.cancel()
	frappe.db.commit()
	return {"ok": 1}


@frappe.whitelist()
def recent_entries():
	return frappe.get_all(
		"Stock Entry",
		fields=["name", "entry_type", "from_warehouse", "to_warehouse", "docstatus", "creation"],
		order_by="creation desc",
		limit_page_length=30,
	)


def seed():
	if not frappe.db.exists("Warehouse", "Kho chính"):
		frappe.get_doc(
			{"doctype": "Warehouse", "warehouse_name": "Kho chính", "is_group": 0}
		).insert(ignore_permissions=True)
		frappe.db.commit()
