"""Chatwoot webhook -> Frappe lead.

Endpoint: POST /api/method/pushesale.api.chatwoot.webhook?secret=<CHATWOOT_WEBHOOK_SECRET>
Events handled:
- message_created with message_type == incoming
- conversation_created (if payload has a contact)
"""

import hmac

import frappe

from pushesale.api import http as http_api
from pushesale.api.lead import upsert_lead
from pushesale.api.settings import (
	conf_value,
	get_password_field,
	get_settings_doc,
	require_settings_role,
)
from pushesale.phone import extract_vn_phones, normalize_vn

CONTACTS_PAGE_LIMIT = 3


def _conf(key):
	return conf_value(key)


def _site_secret():
	return _conf("CHATWOOT_WEBHOOK_SECRET")


def is_valid_secret(provided):
	"""Compare provided secret with settings or site config."""
	if not provided:
		return False
	provided = str(provided)
	candidates = []
	settings_secret = _site_secret()
	if settings_secret:
		candidates.append(str(settings_secret))
	try:
		conf_secret = frappe.conf.get("CHATWOOT_WEBHOOK_SECRET") if hasattr(frappe, "conf") else ""
		if conf_secret:
			candidates.append(str(conf_secret))
	except Exception:
		pass
	seen = set()
	for candidate in candidates:
		if not candidate or candidate in seen:
			continue
		seen.add(candidate)
		if hmac.compare_digest(provided, candidate):
			return True
	return False


def _as_text(value):
	if value is None:
		return ""
	if isinstance(value, str):
		return value
	return str(value)


def parse_chatwoot_payload(payload):
	"""Extract normalized fields from a Chatwoot webhook payload.

	Returns dict with: event, contact_id, contact_name, phone_e164,
	conversation_id, inbox_name, content, account_id. Missing values are "".
	Defensive: Chatwoot payload shape varies by version/channel.
	"""
	payload = payload or {}
	event = payload.get("event") or ""

	contact = payload.get("contact") or payload.get("sender") or {}
	if not isinstance(contact, dict):
		contact = {}
	conv = payload.get("conversation") or {}
	if not isinstance(conv, dict):
		conv = {}
	inbox = payload.get("inbox") or conv.get("inbox") or {}
	if not isinstance(inbox, dict):
		inbox = {}
	account = payload.get("account") or {}
	if not isinstance(account, dict):
		account = {}

	contact_id = _as_text(contact.get("id"))
	contact_name = _as_text(contact.get("name"))
	phone = normalize_vn(contact.get("phone_number") or "")
	content = _as_text(payload.get("content"))
	if not phone and content:
		phones = extract_vn_phones(content)
		phone = phones[0] if phones else ""

	conversation_id = _as_text(conv.get("display_id") or conv.get("id"))
	inbox_name = _as_text(inbox.get("name"))
	account_id = _as_text(account.get("id"))
	message_type = _as_text(payload.get("message_type"))

	return {
		"event": event,
		"message_type": message_type,
		"contact_id": contact_id,
		"contact_name": contact_name,
		"phone_e164": phone or "",
		"conversation_id": conversation_id,
		"inbox_name": inbox_name,
		"content": content,
		"account_id": account_id,
	}


def handle_event(payload):
	"""Core logic (no request context needed). Returns result dict."""
	parsed = parse_chatwoot_payload(payload)
	event = parsed["event"]

	if event == "message_created" and parsed["message_type"] != "incoming":
		return {"ok": True, "skipped": "not-incoming"}

	if event not in ("message_created", "conversation_created"):
		return {"ok": True, "skipped": f"unsupported-event:{event}"}

	if not parsed["contact_id"] and not parsed["phone_e164"] and not parsed["content"]:
		return {"ok": True, "skipped": "empty-payload"}

	external_id = f"chatwoot:{parsed['contact_id']}" if parsed["contact_id"] else None
	lead_name = upsert_lead(
		{
			"external_id": external_id,
			"phone": parsed["phone_e164"],
			"chatwoot_contact_id": parsed["contact_id"] or None,
			"chatwoot_conversation_id": parsed["conversation_id"] or None,
			"name": parsed["contact_name"],
			"source": "Chatwoot",
			"source_detail": parsed["inbox_name"] or None,
			"raw_text": parsed["content"] or None,
		}
	)

	note_back_result = push_lead_reference(
		account_id=parsed["account_id"],
		contact_id=parsed["contact_id"],
		lead_name=lead_name,
	)
	return {"ok": True, "lead": lead_name, "note_back": note_back_result}


def push_lead_reference(account_id, contact_id, lead_name):
	"""Best-effort: set Chatwoot contact custom attribute frappe_lead.

	Skipped silently when CHATWOOT_URL / token / ids are missing.
	Returns True on HTTP 2xx, False otherwise (never raises).
	"""
	if frappe.flags.in_test and not getattr(frappe.flags, "pushesale_note_back", False):
		return False
	base = _conf("CHATWOOT_URL").rstrip("/")
	token = _conf("CHATWOOT_API_TOKEN")
	account_id = (account_id or _conf("CHATWOOT_ACCOUNT_ID")).strip()
	if not (base and token and account_id and contact_id and lead_name):
		return False
	try:
		url = f"{base}/api/v1/accounts/{account_id}/contacts/{contact_id}/custom_attributes"
		status, _data = http_api.http_json(
			"POST",
			url,
			headers={"api_access_token": token},
			json_body={"custom_attributes": {"frappe_lead": lead_name}},
		)
		return 200 <= status < 300
	except Exception:
		frappe.log_error("pushesale chatwoot note-back failed")
		return False


def chatwoot_conversation_url(conversation_id):
	"""Build the agent-facing Chatwoot URL for a conversation (for README/UI)."""
	base = (_conf("CHATWOOT_URL") or "").rstrip("/")
	account_id = (_conf("CHATWOOT_ACCOUNT_ID") or "").strip()
	if not (base and account_id and conversation_id):
		return ""
	return f"{base}/app/accounts/{account_id}/conversations/{conversation_id}"


@frappe.whitelist()
def open_conversation(lead):
	"""URL for the sale to open this lead's Chatwoot thread (or the inbox)."""
	if not lead or not frappe.db.exists("CRM Lead", lead):
		frappe.throw("Không thấy lead")
	if not frappe.has_permission("CRM Lead", "read", lead):
		frappe.throw("Không có quyền", frappe.PermissionError)
	base = (_conf("CHATWOOT_URL") or "").rstrip("/")
	account_id = (_conf("CHATWOOT_ACCOUNT_ID") or "").strip()
	if not base or not account_id:
		frappe.throw("Chưa kết nối Chatwoot. Vào Kênh để điền URL và Account ID.")
	conv = frappe.db.get_value("CRM Lead", lead, "custom_chatwoot_conversation_id")
	if conv:
		url = f"{base}/app/accounts/{account_id}/conversations/{conv}"
	else:
		url = f"{base}/app/accounts/{account_id}"
	return {"url": url, "has_conversation": bool(conv)}


def _chatwoot_creds():
	base = (_conf("CHATWOOT_URL") or "").rstrip("/")
	token = _conf("CHATWOOT_API_TOKEN")
	account_id = (_conf("CHATWOOT_ACCOUNT_ID") or "").strip()
	return base, token, account_id


def _upsert_contact(contact, inbox_name="Chatwoot"):
	contact = contact or {}
	contact_id = _as_text(contact.get("id"))
	name = _as_text(contact.get("name"))
	phone = normalize_vn(contact.get("phone_number") or "")
	if not phone:
		content = _as_text(contact.get("identifier") or "")
		phones = extract_vn_phones(content)
		phone = phones[0] if phones else ""
	if not phone:
		return None, "no-phone"
	existed = False
	if contact_id:
		existed = bool(
			frappe.db.exists("CRM Lead", {"custom_external_id": f"chatwoot:{contact_id}"})
		)
	if not existed and phone:
		existed = bool(frappe.db.exists("CRM Lead", {"custom_phone_e164": phone}))
	lead = upsert_lead(
		{
			"external_id": f"chatwoot:{contact_id}" if contact_id else None,
			"phone": phone,
			"chatwoot_contact_id": contact_id or None,
			"name": name,
			"source": "Chatwoot",
			"source_detail": inbox_name,
		}
	)
	return lead, "merged" if existed else "created"


def _sync_inbox():
	base, token, account_id = _chatwoot_creds()
	if not (base and token and account_id):
		return {"ok": False, "error": "Chưa đủ Chatwoot URL / Account ID / token."}
	stats = {"ok": True, "created": 0, "merged": 0, "skipped_no_phone": 0, "contacts": 0}
	headers = {"api_access_token": token}
	for page in range(1, CONTACTS_PAGE_LIMIT + 1):
		url = f"{base}/api/v1/accounts/{account_id}/contacts"
		status, data = http_api.http_json("GET", url, headers=headers, params={"page": page})
		if status != 200:
			msg = (data or {}).get("error") or (data or {}).get("message") or f"HTTP {status}"
			frappe.throw(f"Chatwoot lỗi: {msg}", frappe.ValidationError)
		payload = (data or {}).get("payload") or (data or {}).get("data") or []
		if isinstance(payload, dict):
			payload = payload.get("payload") or []
		if not payload:
			break
		for contact in payload:
			stats["contacts"] += 1
			_lead, kind = _upsert_contact(contact)
			if kind == "no-phone":
				stats["skipped_no_phone"] += 1
			elif kind == "merged":
				stats["merged"] += 1
			else:
				stats["created"] += 1
		if len(payload) < 5:
			break
	summary = (
		f"Đồng bộ inbox: {stats['created']} lead mới, {stats['merged']} trùng, "
		f"{stats['skipped_no_phone']} bỏ (không SĐT), {stats['contacts']} contact."
	)
	try:
		doc = get_settings_doc()
		doc.chatwoot_last_sync = frappe.utils.now_datetime()
		doc.chatwoot_last_result = summary
		doc.save(ignore_permissions=True)
	except Exception:
		pass
	stats["result"] = summary
	return stats


@frappe.whitelist()
def test_connection(chatwoot_url=None, chatwoot_api_token=None, chatwoot_account_id=None):
	require_settings_role()
	base = (chatwoot_url if chatwoot_url is not None else _conf("CHATWOOT_URL") or "").rstrip("/")
	token = chatwoot_api_token
	if not token or str(token).startswith("****"):
		token = _conf("CHATWOOT_API_TOKEN")
	account_id = (
		chatwoot_account_id if chatwoot_account_id is not None else _conf("CHATWOOT_ACCOUNT_ID")
	)
	if not (base and token):
		frappe.throw("Chưa có Chatwoot URL hoặc API token.", frappe.ValidationError)
	status, data = http_api.http_json(
		"GET", f"{base}/api/v1/profile", headers={"api_access_token": str(token).strip()}
	)
	if status != 200:
		msg = (data or {}).get("error") or (data or {}).get("message") or f"HTTP {status}"
		frappe.throw(f"Không kết nối được Chatwoot: {msg}", frappe.ValidationError)
	name = (data or {}).get("name") or (data or {}).get("email") or ""
	if chatwoot_url is not None or (
		chatwoot_api_token and not str(chatwoot_api_token).startswith("****")
	) or chatwoot_account_id is not None:
		doc = get_settings_doc()
		if chatwoot_url is not None:
			doc.chatwoot_url = str(chatwoot_url).strip()
		if chatwoot_api_token and not str(chatwoot_api_token).startswith("****"):
			doc.chatwoot_api_token = str(chatwoot_api_token).strip()
		if chatwoot_account_id is not None:
			doc.chatwoot_account_id = str(chatwoot_account_id).strip()
		doc.save(ignore_permissions=True)
	return {"ok": True, "name": name, "account_id": str(account_id or "")}


@frappe.whitelist()
def sync_inbox():
	require_settings_role()
	return _sync_inbox()


def scheduled_sync():
	try:
		enabled = int(frappe.db.get_single_value("Pushesale Settings", "chatwoot_sync_enabled") or 0)
		if not enabled:
			return {"ok": True, "skipped": "disabled"}
		return _sync_inbox()
	except Exception:
		frappe.log_error("pushesale chatwoot scheduled_sync failed")
		return {"ok": False}


@frappe.whitelist(allow_guest=True)
def webhook():
	"""Public webhook entry. Secret via ?secret= query param."""
	provided = frappe.request.args.get("secret") if frappe.request else None
	if not is_valid_secret(provided):
		frappe.throw("Invalid webhook secret", frappe.PermissionError)
	try:
		payload = frappe.request.get_json() if frappe.request else {}
	except Exception:
		payload = {}
	if not isinstance(payload, dict):
		payload = {}
	return handle_event(payload)
