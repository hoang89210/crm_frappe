"""Chatwoot webhook -> Frappe lead.

Endpoint: POST /api/method/pushesale.api.chatwoot.webhook?secret=<CHATWOOT_WEBHOOK_SECRET>
Events handled:
- message_created with message_type == "incoming"
- conversation_created (if payload has a contact)
"""

import hmac

import frappe

from pushesale.api.lead import upsert_lead
from pushesale.phone import extract_vn_phones, normalize_vn


def _conf(key):
	# frappe.conf (not get_site_config) so tests can override at runtime.
	return (frappe.conf.get(key) if hasattr(frappe, "conf") else "") or ""


def _site_secret():
	return _conf("CHATWOOT_WEBHOOK_SECRET")


def is_valid_secret(provided):
	"""Compare provided secret with site config using constant-time compare."""
	if not provided:
		return False
	return hmac.compare_digest(str(provided), str(_site_secret()))


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
	base = _conf("CHATWOOT_URL").rstrip("/")
	token = _conf("CHATWOOT_API_TOKEN")
	account_id = (account_id or _conf("CHATWOOT_ACCOUNT_ID")).strip()
	if not (base and token and account_id and contact_id and lead_name):
		return False
	try:
		import requests

		url = f"{base}/api/v1/accounts/{account_id}/contacts/{contact_id}/custom_attributes"
		resp = requests.post(
			url,
			headers={"api_access_token": token},
			json={"custom_attributes": {"frappe_lead": lead_name}},
			timeout=10,
		)
		return 200 <= resp.status_code < 300
	except Exception:
		frappe.log_error("pushesale chatwoot note-back failed")
		return False


def chatwoot_conversation_url(conversation_id):
	"""Build the agent-facing Chatwoot URL for a conversation (for README/UI)."""
	base = _conf("CHATWOOT_URL").rstrip("/")
	account_id = _conf("CHATWOOT_ACCOUNT_ID").strip()
	if not (base and account_id and conversation_id):
		return ""
	return f"{base}/app/accounts/{account_id}/conversations/{conversation_id}"


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
