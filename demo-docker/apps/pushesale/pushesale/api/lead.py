"""Single entry point against duplicate leads.

Lookup order: custom_external_id -> custom_phone_e164 -> custom_chatwoot_contact_id.
Existing lead: fill empty fields only, never overwrite a non-'Moi' care status.
New lead: CRM status 'New', care status 'Moi'.
"""

import frappe

from pushesale.phone import display_vn, normalize_vn


def _ensure_source(source_name):
	if not source_name:
		return None
	if frappe.db.exists("CRM Lead Source", source_name):
		return source_name
	doc = frappe.get_doc({"doctype": "CRM Lead Source", "source_name": source_name})
	doc.insert(ignore_permissions=True)
	return source_name


def upsert_lead(payload):
	"""Create or update a CRM Lead. Returns lead name.

	payload keys: external_id, phone (any VN format), chatwoot_contact_id,
	chatwoot_conversation_id, name (full name), first_name, source,
	source_detail, raw_text, owner (user id / lead_owner), team.
	"""
	payload = dict(payload or {})
	external_id = (payload.get("external_id") or "").strip() or None
	chatwoot_contact_id = (payload.get("chatwoot_contact_id") or "").strip() or None
	phone_e164 = normalize_vn(payload.get("phone") or payload.get("phone_e164") or "")

	lead_name = None
	if external_id:
		lead_name = frappe.db.get_value("CRM Lead", {"custom_external_id": external_id}, "name")
	if not lead_name and phone_e164:
		lead_name = frappe.db.get_value("CRM Lead", {"custom_phone_e164": phone_e164}, "name")
	if not lead_name and chatwoot_contact_id:
		lead_name = frappe.db.get_value(
			"CRM Lead", {"custom_chatwoot_contact_id": chatwoot_contact_id}, "name"
		)

	if lead_name:
		doc = frappe.get_doc("CRM Lead", lead_name)
		changed = False
		fill_map = {
			"custom_external_id": external_id,
			"custom_phone_e164": phone_e164,
			"custom_chatwoot_contact_id": chatwoot_contact_id,
			"custom_chatwoot_conversation_id": (
				payload.get("chatwoot_conversation_id") or ""
			).strip()
			or None,
			"custom_source_detail": (payload.get("source_detail") or "").strip() or None,
			"custom_fb_page_id": (payload.get("fb_page_id") or "").strip() or None,
			"custom_fb_page_name": (payload.get("fb_page_name") or "").strip() or None,
			"custom_raw_text": (payload.get("raw_text") or "").strip() or None,
			"custom_team": (payload.get("team") or "").strip() or None,
			"lead_owner": (payload.get("owner") or "").strip() or None,
		}
		for field, value in fill_map.items():
			if value and not doc.get(field):
				doc.set(field, value)
				changed = True
		if phone_e164 and not doc.get("mobile_no"):
			doc.mobile_no = display_vn(phone_e164)
			changed = True
		if changed:
			doc.save(ignore_permissions=True)
		return doc.name

	full_name = (payload.get("name") or payload.get("first_name") or "").strip()
	first_name = full_name.split(" ")[0] if full_name else "Unknown"
	source = _ensure_source((payload.get("source") or "").strip() or None)
	doc = frappe.get_doc(
		{
			"doctype": "CRM Lead",
			"first_name": first_name,
			"lead_name": full_name or first_name,
			"mobile_no": display_vn(phone_e164) if phone_e164 else "",
			"status": "New",
			"source": source,
			"lead_owner": (payload.get("owner") or "").strip() or None,
			"custom_source_detail": (payload.get("source_detail") or "").strip() or None,
			"custom_fb_page_id": (payload.get("fb_page_id") or "").strip() or None,
			"custom_fb_page_name": (payload.get("fb_page_name") or "").strip() or None,
			"custom_chatwoot_contact_id": chatwoot_contact_id,
			"custom_chatwoot_conversation_id": (
				payload.get("chatwoot_conversation_id") or ""
			).strip()
			or None,
			"custom_external_id": external_id,
			"custom_phone_e164": phone_e164,
			"custom_care_status": "Mới",
			"custom_care_count": 0,
			"custom_team": (payload.get("team") or "").strip() or None,
			"custom_raw_text": (payload.get("raw_text") or "").strip() or None,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name
