"""Manual lead reassignment (Sales Manager / System Manager only).

- Find lead by name OR by VN phone (custom_phone_e164).
- New owner must be an enabled user with a Sales role.
- Changing lead_owner triggers CRM's built-in share_with_agent / assign_agent.
- A Comment is logged on the lead: old -> new + reason.
"""

import frappe

from pushesale.phone import normalize_vn

MANAGER_ROLES = {"System Manager", "Sales Manager"}
SALES_ROLES = {"System Manager", "Sales Manager", "Sales User"}


def _require_manager(user):
	if user == "Administrator":
		return
	if not (set(frappe.get_roles(user)) & MANAGER_ROLES):
		frappe.throw("Chỉ Sales Manager được chuyển lead.", frappe.PermissionError)


def _resolve_lead(lead=None, phone=None):
	if lead:
		if not frappe.db.exists("CRM Lead", lead):
			frappe.throw(f"Lead {lead} không tồn tại.")
		return lead
	if phone:
		e164 = normalize_vn(phone)
		if not e164:
			frappe.throw(f"SĐT không hợp lệ: {phone}")
		names = frappe.get_all("CRM Lead", filters={"custom_phone_e164": e164}, pluck="name")
		if not names:
			frappe.throw(f"Không tìm thấy lead có SĐT {phone}.")
		if len(names) > 1:
			frappe.throw(
				f"SĐT {phone} trùng {len(names)} lead, chỉ định rõ mã lead: {', '.join(names[:5])}"
			)
		return names[0]
	frappe.throw("Thiếu lead hoặc phone.")


@frappe.whitelist()
def reassign_lead(lead=None, phone=None, new_owner=None, ly_do=None):
	"""Chuyển lead sang Sale khác. Returns dict with old/new owner."""
	user = frappe.session.user
	if user in ("Guest", None):
		frappe.throw("Login required", frappe.PermissionError)
	_require_manager(user)

	new_owner = (new_owner or "").strip()
	if not new_owner or not frappe.db.exists("User", new_owner):
		frappe.throw(f"Tài khoản {new_owner or '?'} không tồn tại.")
	target = frappe.get_doc("User", new_owner)
	if not target.enabled:
		frappe.throw(f"Tài khoản {new_owner} đang tắt.")
	if new_owner != "Administrator" and not (set(frappe.get_roles(new_owner)) & SALES_ROLES):
		frappe.throw(f"Tài khoản {new_owner} không phải Sales.")

	lead_name = _resolve_lead(lead, phone)
	doc = frappe.get_doc("CRM Lead", lead_name)
	old_owner = doc.get("lead_owner") or ""
	if old_owner == new_owner:
		return {"ok": True, "unchanged": True, "lead": lead_name, "owner": new_owner}

	# Order matters (CRM mirrors assignment <-> owner):
	# 1. Cancel the old owner's open assignment ToDos FIRST. CRM clears the
	#    owner on cancel; it also notifies the old owner their assignment ended.
	# 2. Set the new owner and save. CRM auto-assigns + shares with the new owner.
	if old_owner and old_owner != new_owner:
		for todo_name in frappe.get_all(
			"ToDo",
			filters={
				"reference_type": "CRM Lead",
				"reference_name": lead_name,
				"allocated_to": old_owner,
				"status": ["!=", "Cancelled"],
			},
			pluck="name",
		):
			todo = frappe.get_doc("ToDo", todo_name)
			todo.status = "Cancelled"
			todo.save(ignore_permissions=True)
	doc.lead_owner = new_owner
	doc.save()
	frappe.get_doc(
		{
			"doctype": "Comment",
			"comment_type": "Comment",
			"reference_doctype": "CRM Lead",
			"reference_name": lead_name,
			"comment_email": user,
			"content": (
				f"Chuyển lead từ {old_owner or '(chưa có)'} → {new_owner}."
				+ (f" Lý do: {ly_do}" if (ly_do or '').strip() else "")
			),
		}
	).insert(ignore_permissions=True)
	return {"ok": True, "lead": lead_name, "old_owner": old_owner, "new_owner": new_owner}
