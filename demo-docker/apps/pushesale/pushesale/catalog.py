import frappe


FIELDS = [
	{
		"dt": "CRM Product",
		"fieldname": "custom_category",
		"fieldtype": "Link",
		"label": "Danh mục",
		"options": "Product Category",
		"insert_after": "product_name",
		"in_list_view": 1,
		"in_standard_filter": 1,
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_uom",
		"fieldtype": "Data",
		"label": "Đơn vị tính",
		"insert_after": "custom_category",
		"in_list_view": 1,
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_weight_kg",
		"fieldtype": "Float",
		"label": "Khối lượng (kg)",
		"insert_after": "custom_uom",
		"precision": "3",
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_length_cm",
		"fieldtype": "Float",
		"label": "Dài (cm)",
		"insert_after": "custom_weight_kg",
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_width_cm",
		"fieldtype": "Float",
		"label": "Rộng (cm)",
		"insert_after": "custom_length_cm",
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_height_cm",
		"fieldtype": "Float",
		"label": "Cao (cm)",
		"insert_after": "custom_width_cm",
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_is_combo",
		"fieldtype": "Check",
		"label": "Là combo",
		"insert_after": "product_name",
		"default": "0",
	},
	{
		"dt": "CRM Product",
		"fieldname": "custom_short_description",
		"fieldtype": "Small Text",
		"label": "Mô tả ngắn",
		"insert_after": "description",
	},
]

CATEGORIES = [
	("Mỹ phẩm", None, 1),
	("Son môi", "Mỹ phẩm", 0),
	("Kem dưỡng", "Mỹ phẩm", 0),
	("Thực phẩm", None, 1),
	("Bánh", "Thực phẩm", 0),
	("Trà", "Thực phẩm", 0),
]

PRODUCTS = [
	{
		"product_code": "SON-DO",
		"product_name": "Son đỏ",
		"standard_rate": 150000,
		"custom_category": "Son môi",
		"custom_uom": "cái",
		"custom_weight_kg": 0.05,
		"custom_short_description": "Son lì đỏ",
	},
	{
		"product_code": "SON-NUDE",
		"product_name": "Son nude",
		"standard_rate": 180000,
		"custom_category": "Son môi",
		"custom_uom": "cái",
		"custom_weight_kg": 0.05,
		"custom_short_description": "Son nude hồng",
	},
	{
		"product_code": "KEM-AM",
		"product_name": "Kem dưỡng ẩm",
		"standard_rate": 250000,
		"custom_category": "Kem dưỡng",
		"custom_uom": "hộp",
		"custom_weight_kg": 0.2,
		"custom_short_description": "Kem dưỡng da mặt",
	},
	{
		"product_code": "KEM-CN",
		"product_name": "Kem chống nắng",
		"standard_rate": 220000,
		"custom_category": "Kem dưỡng",
		"custom_uom": "hộp",
		"custom_weight_kg": 0.15,
		"custom_short_description": "SPF50",
	},
	{
		"product_code": "BANH-QY",
		"product_name": "Bánh quy",
		"standard_rate": 45000,
		"custom_category": "Bánh",
		"custom_uom": "hộp",
		"custom_weight_kg": 0.3,
		"custom_short_description": "Bánh quy bơ",
	},
	{
		"product_code": "TRA-XANH",
		"product_name": "Trà xanh",
		"standard_rate": 89000,
		"custom_category": "Trà",
		"custom_uom": "hộp",
		"custom_weight_kg": 0.2,
		"custom_short_description": "Trà xanh túi lọc",
	},
]


def ensure_fields():
	for row in FIELDS:
		name = f"{row['dt']}-{row['fieldname']}"
		if frappe.db.exists("Custom Field", name):
			continue
		doc = frappe.get_doc({"doctype": "Custom Field", **row})
		doc.insert(ignore_permissions=True)
	frappe.clear_cache(doctype="CRM Product")


def ensure_category(name, parent, is_group):
	if frappe.db.exists("Product Category", name):
		doc = frappe.get_doc("Product Category", name)
		changed = False
		if parent and doc.parent_product_category != parent:
			doc.parent_product_category = parent
			changed = True
		if int(doc.is_group or 0) != int(is_group):
			doc.is_group = is_group
			changed = True
		if changed:
			doc.save(ignore_permissions=True)
		return
	frappe.get_doc(
		{
			"doctype": "Product Category",
			"category_name": name,
			"parent_product_category": parent,
			"is_group": is_group,
		}
	).insert(ignore_permissions=True)


def ensure_product(row):
	if frappe.db.exists("CRM Product", row["product_code"]):
		doc = frappe.get_doc("CRM Product", row["product_code"])
		for key, value in row.items():
			doc.set(key, value)
		doc.save(ignore_permissions=True)
		return
	frappe.get_doc({"doctype": "CRM Product", **row}).insert(ignore_permissions=True)


def _text(value):
	if value is None or isinstance(value, (dict, list)):
		return ""
	return str(value).strip()


def _flag(value):
	if isinstance(value, bool):
		return int(value)
	if isinstance(value, (int, float)) and not isinstance(value, bool):
		return 1 if int(value) else 0
	text = _text(value).lower()
	return 1 if text in ("1", "true", "yes") else 0


def _num(value, default=0):
	if isinstance(value, (dict, list)):
		return float(default)
	try:
		return float(value if value not in (None, "") else default)
	except (TypeError, ValueError):
		return float(default)


def _lines(raw):
	if isinstance(raw, list):
		return [row for row in raw if isinstance(row, dict)]
	if isinstance(raw, dict):
		frappe.throw("Dòng combo không hợp lệ")
	try:
		rows = frappe.parse_json(raw or "[]")
	except Exception:
		frappe.throw("Dòng combo không hợp lệ")
	if not isinstance(rows, list):
		frappe.throw("Dòng combo không hợp lệ")
	return [row for row in rows if isinstance(row, dict)]


def _descendants(name):
	"""Return all descendant names of a Product Category (any depth)."""
	out = []
	queue = [name]
	while queue:
		parent = queue.pop(0)
		children = frappe.get_all(
			"Product Category",
			filters={"parent_product_category": parent},
			pluck="name",
		)
		for child in children:
			if child in out:
				continue
			out.append(child)
			queue.append(child)
	return out


@frappe.whitelist()
def save_category(old_name=None, category_name=None, parent=None, is_group=0):
	category_name = _text(category_name)
	old_name = _text(old_name) or None
	parent = _text(parent) or None
	if not category_name:
		frappe.throw("Nhập tên danh mục")
	if parent and parent in (category_name, old_name):
		frappe.throw("Không chọn chính nó làm cha")
	if parent and old_name and frappe.db.exists("Product Category", old_name):
		if parent in _descendants(old_name):
			frappe.throw("Không chọn danh mục con làm cha")
	is_group = _flag(is_group)
	if old_name and frappe.db.exists("Product Category", old_name):
		doc = frappe.get_doc("Product Category", old_name)
		doc.is_group = is_group
		doc.parent_product_category = parent
		doc.save(ignore_permissions=True)
		if category_name != old_name:
			frappe.rename_doc("Product Category", old_name, category_name, force=True)
		frappe.db.commit()
		return {"name": category_name}
	if frappe.db.exists("Product Category", category_name):
		frappe.throw("Danh mục đã tồn tại")
	doc = frappe.get_doc(
		{
			"doctype": "Product Category",
			"category_name": category_name,
			"parent_product_category": parent,
			"is_group": is_group,
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist()
def delete_category(name):
	name = _text(name)
	if not name or not frappe.db.exists("Product Category", name):
		frappe.throw("Không thấy danh mục")
	if frappe.db.exists("Product Category", {"parent_product_category": name}):
		frappe.throw("Còn danh mục con, không xóa được")
	if frappe.db.exists("CRM Product", {"custom_category": name}):
		frappe.throw("Còn sản phẩm trong danh mục, không xóa được")
	frappe.delete_doc("Product Category", name, ignore_permissions=True, force=1)
	frappe.db.commit()
	return {"ok": 1}


def _replace_combo_lines(code, lines):
	for row in frappe.get_all("Product Combo Line", filters={"combo": code}, pluck="name"):
		frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
	retail = 0
	for raw in lines:
		if not isinstance(raw, dict):
			continue
		item = _text(raw.get("item"))
		qty = _num(raw.get("qty"), 1)
		if not item:
			continue
		if item == code:
			frappe.throw("Combo không chứa chính nó")
		if not frappe.db.exists("CRM Product", item):
			frappe.throw(f"Không thấy sản phẩm {item}")
		if int(frappe.db.get_value("CRM Product", item, "custom_is_combo") or 0):
			frappe.throw(f"{item} là combo, không gắn lồng")
		if qty <= 0:
			frappe.throw("Số lượng phải lớn hơn 0")
		frappe.get_doc(
			{"doctype": "Product Combo Line", "combo": code, "item": item, "qty": qty}
		).insert(ignore_permissions=True)
		rate = _num(frappe.db.get_value("CRM Product", item, "standard_rate"))
		retail += rate * qty
	return retail


@frappe.whitelist()
def get_combo_lines(combo):
	combo = _text(combo)
	rows = frappe.get_all(
		"Product Combo Line",
		filters={"combo": combo},
		fields=["name", "item", "qty"],
		order_by="creation asc",
	)
	for row in rows:
		row["item_name"] = frappe.db.get_value("CRM Product", row.item, "product_name")
		row["rate"] = _num(frappe.db.get_value("CRM Product", row.item, "standard_rate"))
	return rows


@frappe.whitelist()
def save_product(
	old_code=None,
	product_code=None,
	product_name=None,
	custom_category=None,
	custom_uom=None,
	custom_weight_kg=0,
	custom_length_cm=0,
	custom_width_cm=0,
	custom_height_cm=0,
	standard_rate=0,
	custom_short_description=None,
	custom_is_combo=0,
	lines=None,
):
	product_code = _text(product_code)
	product_name = _text(product_name)
	old_code = _text(old_code) or None
	custom_category = _text(custom_category) or None
	if not product_code or not product_name:
		frappe.throw("Nhập mã và tên sản phẩm")
	is_combo = _flag(custom_is_combo)
	parsed = _lines(lines)
	if is_combo and not any(_text(r.get("item")) for r in parsed):
		frappe.throw("Combo cần ít nhất 1 sản phẩm lẻ")
	payload = {
		"product_name": product_name,
		"custom_category": custom_category or None,
		"custom_uom": _text(custom_uom),
		"custom_weight_kg": _num(custom_weight_kg),
		"custom_length_cm": _num(custom_length_cm),
		"custom_width_cm": _num(custom_width_cm),
		"custom_height_cm": _num(custom_height_cm),
		"standard_rate": _num(standard_rate),
		"custom_short_description": _text(custom_short_description),
		"custom_is_combo": is_combo,
	}
	if old_code and frappe.db.exists("CRM Product", old_code):
		doc = frappe.get_doc("CRM Product", old_code)
		doc.update(payload)
		doc.save(ignore_permissions=True)
		if product_code != old_code:
			frappe.rename_doc("CRM Product", old_code, product_code, force=True)
			code = product_code
		else:
			code = old_code
	else:
		if frappe.db.exists("CRM Product", product_code):
			frappe.throw("Mã sản phẩm đã tồn tại")
		doc = frappe.get_doc({"doctype": "CRM Product", "product_code": product_code, **payload})
		doc.insert(ignore_permissions=True)
		code = doc.name
	retail = _replace_combo_lines(code, parsed if is_combo else [])
	frappe.db.commit()
	return {"name": code, "retail_total": retail}


@frappe.whitelist()
def delete_product(name, detach_combo=0, confirm_combo=0):
	name = _text(name)
	if not name or not frappe.db.exists("CRM Product", name):
		frappe.throw("Không thấy sản phẩm")
	combos = frappe.get_all("Product Combo Line", filters={"item": name}, pluck="combo")
	if combos and not _flag(detach_combo):
		frappe.throw("Đang trong combo: " + ", ".join(combos) + ". Gỡ khỏi combo rồi xóa?")
	if frappe.db.table_exists("CRM Products") and frappe.db.exists("CRM Products", {"product_code": name}):
		frappe.throw("Sản phẩm đang gắn Lead/Deal, không xóa được")
	if int(frappe.db.get_value("CRM Product", name, "custom_is_combo") or 0) and not _flag(confirm_combo):
		count = frappe.db.count("Product Combo Line", {"combo": name})
		frappe.throw(f"Combo này chứa {count} sản phẩm lẻ. Bạn có chắc muốn xóa?")
	for row in frappe.get_all("Product Combo Line", filters={"item": name}, pluck="name"):
		frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
	for row in frappe.get_all("Product Combo Line", filters={"combo": name}, pluck="name"):
		frappe.delete_doc("Product Combo Line", row, ignore_permissions=True, force=1)
	frappe.delete_doc("CRM Product", name, ignore_permissions=True, force=1)
	frappe.db.commit()
	return {"ok": 1}


HEADERS = {
	"product_code": "product_code",
	"ma": "product_code",
	"mã": "product_code",
	"product_name": "product_name",
	"ten": "product_name",
	"tên": "product_name",
	"category": "category",
	"danh_muc": "category",
	"danh mục": "category",
	"uom": "uom",
	"dvt": "uom",
	"đvt": "uom",
	"weight_kg": "weight_kg",
	"kg": "weight_kg",
	"rate": "rate",
	"gia": "rate",
	"giá": "rate",
	"short_description": "short_description",
	"mo_ta": "short_description",
	"mô tả": "short_description",
}


def _sample_workbook():
	from io import BytesIO

	from openpyxl import Workbook

	wb = Workbook()
	ws = wb.active
	ws.title = "SanPham"
	ws.append(
		[
			"product_code",
			"product_name",
			"category",
			"uom",
			"weight_kg",
			"rate",
			"short_description",
		]
	)
	ws.append(["SON-MAU", "Sản phẩm mẫu", "Nhóm mẫu", "cái", 0.1, 100000, "Mô tả ngắn"])
	buf = BytesIO()
	wb.save(buf)
	return buf.getvalue()


@frappe.whitelist()
def download_product_template():
	import base64

	raw = _sample_workbook()
	return {
		"filename": "mau-hang-hoa.xlsx",
		"filedata": base64.b64encode(raw).decode(),
	}


def _header_key(cell):
	text = _text(cell).lower().replace(" ", "").replace("_", "")
	for key, value in HEADERS.items():
		if key.replace(" ", "").replace("_", "") == text:
			return value
	return None


@frappe.whitelist()
def import_products(filedata=None):
	import base64
	from io import BytesIO

	from openpyxl import load_workbook

	filedata = _text(filedata)
	if not filedata:
		frappe.throw("Chưa có file Excel")
	try:
		raw = base64.b64decode(filedata)
		wb = load_workbook(BytesIO(raw), data_only=True)
	except Exception:
		frappe.throw("File Excel không đọc được. Dùng mẫu .xlsx.")
	ws = wb.active
	rows = list(ws.iter_rows(values_only=True))
	if not rows:
		frappe.throw("File trống")
	keys = [_header_key(c) for c in rows[0]]
	if "product_code" not in keys or "product_name" not in keys:
		frappe.throw("Thiếu cột product_code hoặc product_name")
	created, updated, skipped = 0, 0, 0
	errors = []
	for idx, row in enumerate(rows[1:], start=2):
		data = {}
		for i, key in enumerate(keys):
			if key and i < len(row):
				data[key] = row[i]
		code = _text(data.get("product_code"))
		name = _text(data.get("product_name"))
		if not code and not name:
			continue
		if not code or not name:
			skipped += 1
			errors.append({"row": idx, "message": "Thiếu mã hoặc tên"})
			continue
		category = _text(data.get("category"))
		try:
			if category and not frappe.db.exists("Product Category", category):
				save_category(category_name=category, is_group=0)
			existed = frappe.db.exists("CRM Product", code)
			if existed and int(frappe.db.get_value("CRM Product", code, "custom_is_combo") or 0):
				skipped += 1
				errors.append({"row": idx, "message": "Là combo, bỏ qua (không import combo)"})
				continue
			save_product(
				old_code=code if existed else None,
				product_code=code,
				product_name=name,
				custom_category=category,
				custom_uom=_text(data.get("uom")) or "cái",
				custom_weight_kg=data.get("weight_kg"),
				standard_rate=data.get("rate"),
				custom_short_description=_text(data.get("short_description")),
				custom_is_combo=0,
				lines="[]",
			)
			if existed:
				updated += 1
			else:
				created += 1
		except Exception as exc:
			skipped += 1
			errors.append({"row": idx, "message": str(exc)[:180]})
	return {
		"created": created,
		"updated": updated,
		"skipped": skipped,
		"errors": errors[:20],
	}


def seed():
	ensure_fields()
	for name, parent, is_group in CATEGORIES:
		ensure_category(name, parent, is_group)
	for row in PRODUCTS:
		ensure_product(row)
	ensure_product(
		{
			"product_code": "COMBO-SON",
			"product_name": "Combo son",
			"standard_rate": 300000,
			"custom_category": "Son môi",
			"custom_uom": "bộ",
			"custom_weight_kg": 0.1,
			"custom_is_combo": 1,
			"custom_short_description": "Son đỏ + son nude, giá set riêng",
		}
	)
	_replace_combo_lines(
		"COMBO-SON",
		[{"item": "SON-DO", "qty": 1}, {"item": "SON-NUDE", "qty": 1}],
	)
	frappe.db.commit()
	print(f"categories={frappe.db.count('Product Category')} products={frappe.db.count('CRM Product')}")


def verify():
	missing = [
		row["fieldname"]
		for row in FIELDS
		if not frappe.get_meta("CRM Product").has_field(row["fieldname"])
	]
	if missing:
		frappe.throw(f"missing fields: {missing}")
	doc = frappe.get_doc("CRM Product", "SON-DO")
	assert doc.custom_category == "Son môi", doc.custom_category
	assert doc.custom_uom == "cái", doc.custom_uom
	assert float(doc.custom_weight_kg) == 0.05, doc.custom_weight_kg
	parent = frappe.db.get_value("Product Category", "Son môi", "parent_product_category")
	assert parent == "Mỹ phẩm", parent
	lead_name = "CATALOG-TEST-LEAD"
	if frappe.db.exists("CRM Lead", lead_name):
		frappe.delete_doc("CRM Lead", lead_name, ignore_permissions=True, force=1)
	lead = frappe.get_doc(
		{
			"doctype": "CRM Lead",
			"first_name": "Catalog",
			"lead_name": "Catalog Test",
			"status": "New",
			"custom_care_status": "Mới",
			"products": [
				{
					"product_code": "SON-DO",
					"product_name": "Son đỏ",
					"qty": 2,
					"rate": 150000,
				}
			],
		}
	)
	lead.insert(ignore_permissions=True)
	lead.reload()
	assert lead.products and lead.products[0].product_code == "SON-DO"
	frappe.delete_doc("CRM Lead", lead.name, ignore_permissions=True, force=1)
	combo = frappe.get_doc("CRM Product", "COMBO-SON")
	assert int(combo.custom_is_combo) == 1
	assert float(combo.standard_rate) == 300000
	lines = frappe.get_all("Product Combo Line", filters={"combo": "COMBO-SON"}, pluck="item")
	assert set(lines) == {"SON-DO", "SON-NUDE"}, lines
	frappe.db.commit()
	print("VERIFY_OK")
