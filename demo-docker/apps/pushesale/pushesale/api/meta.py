"""Facebook comment sync + Meta webhook -> CRM Lead."""

import hashlib
import hmac
import re
from urllib.parse import parse_qs, urlparse

import frappe

from pushesale.api import http as http_api
from pushesale.api.lead import upsert_lead
from pushesale.api.settings import (
	conf_value,
	get_password_field,
	get_settings_doc,
	require_settings_role,
)
from pushesale.phone import extract_vn_phones

GRAPH = "https://graph.facebook.com/v21.0"
FEED_POST_LIMIT = 15
FEED_COMMENT_LIMIT = 25


def parse_facebook_page_ref(raw):
	raw = (raw or "").strip()
	if not raw:
		return ""
	if raw.startswith("@"):
		raw = raw[1:]
	if re.fullmatch(r"\d+", raw):
		return raw
	lower = raw.lower()
	if "facebook.com" not in lower and "fb.com" not in lower and "fb.me" not in lower:
		return raw.split("?")[0].strip("/")
	if "://" not in raw:
		raw = "https://" + raw
	parsed = urlparse(raw)
	qs = parse_qs(parsed.query)
	if qs.get("id"):
		return qs["id"][0]
	parts = [p for p in parsed.path.split("/") if p]
	skip = {"pages", "profile.php", "people", "pg", "p", "groups"}
	parts = [p for p in parts if p.lower() not in skip]
	if not parts:
		return ""
	if parts[-1].isdigit():
		return parts[-1]
	if len(parts) >= 2 and parts[1].lower() in ("posts", "videos", "photos", "reel", "reels"):
		return parts[0]
	return parts[0]


def graph_get(path, token, params=None):
	params = dict(params or {})
	params["access_token"] = token
	url = GRAPH + "/" + str(path).lstrip("/")
	return http_api.http_json("GET", url, params=params)


def _graph_error(data):
	err = (data or {}).get("error") or {}
	return err.get("message") or "Facebook Graph lỗi"


def process_comment(comment, page_id="", page_name=""):
	comment = comment or {}
	message = comment.get("message") or ""
	phones = extract_vn_phones(message)
	if not phones:
		return []
	comment_id = str(comment.get("id") or comment.get("comment_id") or "")
	from_info = comment.get("from") or {}
	from_name = from_info.get("name") or "Facebook"
	source_detail = page_name or page_id or ""
	leads = []
	for phone in phones:
		ext = f"fbcomment:{comment_id}:{phone}" if comment_id else f"fbcomment:{phone}"
		lead = upsert_lead(
			{
				"external_id": ext,
				"phone": phone,
				"name": from_name,
				"source": "Facebook Comment",
				"source_detail": source_detail or None,
				"raw_text": message,
				"fb_page_id": page_id or None,
				"fb_page_name": page_name or None,
			}
		)
		leads.append(lead)
	return leads


def handle_feed_event(payload, page_id="", page_name=""):
	payload = payload or {}
	created = []
	skipped = 0
	entries = payload.get("entry") or []
	if payload.get("item") == "comment" or payload.get("comment_id") or payload.get("message"):
		entries = [{"changes": [{"value": payload, "field": "feed"}]}]
	for entry in entries:
		eid = str((entry or {}).get("id") or page_id or "")
		for change in (entry or {}).get("changes") or []:
			if (change or {}).get("field") not in (None, "feed"):
				continue
			value = (change or {}).get("value") or {}
			item = value.get("item") or ""
			if item and item != "comment":
				continue
			if not (value.get("message") or value.get("comment_id") or value.get("id")):
				continue
			leads = process_comment(value, page_id=eid or page_id, page_name=page_name)
			if leads:
				created.extend(leads)
			else:
				skipped += 1
	return {"ok": True, "leads": created, "skipped_no_phone": skipped}


def verify_meta_signature(raw_body, header_sig, app_secret):
	if not app_secret or not header_sig:
		return False
	header_sig = str(header_sig)
	if not header_sig.startswith("sha256="):
		return False
	if isinstance(raw_body, str):
		raw_body = raw_body.encode("utf-8")
	expected = "sha256=" + hmac.new(
		str(app_secret).encode("utf-8"), raw_body, hashlib.sha256
	).hexdigest()
	return hmac.compare_digest(header_sig, expected)


def handle_verify(mode, token, challenge, expected_token):
	if mode == "subscribe" and expected_token and token == expected_token and challenge:
		return str(challenge)
	frappe.throw("Invalid verify token", frappe.PermissionError)


def resolve_page(token, page_url=""):
	status, me = graph_get("me", token, {"fields": "id,name"})
	if status != 200:
		frappe.throw(_graph_error(me), frappe.ValidationError)
	ref = parse_facebook_page_ref(page_url)
	me_id = str((me or {}).get("id") or "")
	me_name = (me or {}).get("name") or ""
	if not ref or ref == me_id or (me_name and ref.lower() == me_name.lower()):
		return {"id": me_id, "name": me_name}
	status, page = graph_get(ref, token, {"fields": "id,name"})
	if status != 200:
		frappe.throw(_graph_error(page), frappe.ValidationError)
	return {"id": str((page or {}).get("id") or ref), "name": (page or {}).get("name") or me_name}


def _count_upsert(comment, page_id, page_name, stats):
	comment_id = str(comment.get("id") or comment.get("comment_id") or "")
	message = comment.get("message") or ""
	phones = extract_vn_phones(message)
	if not phones:
		stats["skipped_no_phone"] += 1
		return
	from_name = (comment.get("from") or {}).get("name") or "Facebook"
	for phone in phones:
		ext = f"fbcomment:{comment_id}:{phone}" if comment_id else f"fbcomment:{phone}"
		existed = bool(frappe.db.exists("CRM Lead", {"custom_external_id": ext}))
		upsert_lead(
			{
				"external_id": ext,
				"phone": phone,
				"name": from_name,
				"source": "Facebook Comment",
				"source_detail": page_name or page_id or None,
				"raw_text": message,
				"fb_page_id": page_id or None,
				"fb_page_name": page_name or None,
			}
		)
		if existed:
			stats["merged"] += 1
		else:
			stats["created"] += 1


def _sync_facebook():
	token = get_password_field("facebook_access_token")
	if not token:
		return {"ok": False, "error": "Chưa có Facebook access token."}
	doc = get_settings_doc()
	page_id = (doc.facebook_page_id or "").strip()
	page_name = (doc.facebook_page_name or "").strip()
	page_url = (doc.facebook_page_url or "").strip()
	if not page_id:
		info = resolve_page(token, page_url)
		page_id = info["id"]
		page_name = info["name"]
		doc.facebook_page_id = page_id
		doc.facebook_page_name = page_name
	since = None
	if doc.facebook_last_sync:
		try:
			since = int(frappe.utils.get_datetime(doc.facebook_last_sync).timestamp())
		except Exception:
			since = None
	params = {
		"fields": f"id,created_time,comments.limit({FEED_COMMENT_LIMIT}){{id,message,from,created_time}}",
		"limit": FEED_POST_LIMIT,
	}
	if since:
		params["since"] = since
	status, data = graph_get(f"{page_id}/feed", token, params)
	if status != 200:
		frappe.throw(_graph_error(data), frappe.ValidationError)
	stats = {
		"ok": True,
		"created": 0,
		"merged": 0,
		"skipped_no_phone": 0,
		"posts": 0,
		"comments": 0,
	}
	for post in (data or {}).get("data") or []:
		stats["posts"] += 1
		comments = ((post or {}).get("comments") or {}).get("data") or []
		for comment in comments:
			stats["comments"] += 1
			_count_upsert(comment, page_id, page_name, stats)
	summary = (
		f"Đồng bộ xong: {stats['created']} lead mới, {stats['merged']} trùng, "
		f"{stats['skipped_no_phone']} comment bỏ (không SĐT), "
		f"{stats['posts']} bài / {stats['comments']} comment."
	)
	doc.facebook_last_sync = frappe.utils.now_datetime()
	doc.facebook_last_result = summary
	doc.save(ignore_permissions=True)
	stats["result"] = summary
	stats["page_id"] = page_id
	stats["page_name"] = page_name
	return stats


@frappe.whitelist()
def test_connection(facebook_page_url=None, facebook_access_token=None):
	require_settings_role()
	token = facebook_access_token
	if not token or str(token).startswith("****"):
		token = get_password_field("facebook_access_token")
	page_url = facebook_page_url
	if page_url is None:
		page_url = frappe.db.get_single_value("Pushesale Settings", "facebook_page_url") or ""
	if not token:
		frappe.throw("Chưa có Facebook access token.", frappe.ValidationError)
	info = resolve_page(str(token).strip(), str(page_url or "").strip())
	doc = get_settings_doc()
	if facebook_page_url is not None:
		doc.facebook_page_url = str(facebook_page_url).strip()
	if facebook_access_token and not str(facebook_access_token).startswith("****"):
		doc.facebook_access_token = str(facebook_access_token).strip()
	doc.facebook_page_id = info["id"]
	doc.facebook_page_name = info["name"]
	doc.save(ignore_permissions=True)
	return {"ok": True, "page_id": info["id"], "page_name": info["name"]}


@frappe.whitelist()
def sync_recent():
	require_settings_role()
	return _sync_facebook()


def scheduled_sync():
	try:
		enabled = int(frappe.db.get_single_value("Pushesale Settings", "facebook_sync_enabled") or 0)
		if not enabled:
			return {"ok": True, "skipped": "disabled"}
		if not get_password_field("facebook_access_token"):
			return {"ok": True, "skipped": "no-token"}
		return _sync_facebook()
	except Exception:
		frappe.log_error("pushesale facebook scheduled_sync failed")
		return {"ok": False}


@frappe.whitelist(allow_guest=True)
def webhook():
	req = frappe.request
	if req and req.method == "GET":
		form = frappe.form_dict or {}
		mode = form.get("hub.mode") or form.get("hub_mode")
		token = form.get("hub.verify_token") or form.get("hub_verify_token")
		challenge = form.get("hub.challenge") or form.get("hub_challenge")
		expected = conf_value("META_VERIFY_TOKEN")
		text = handle_verify(mode, token, challenge, expected)
		frappe.local.response["type"] = "txt"
		frappe.local.response["message"] = text
		return text

	app_secret = conf_value("META_APP_SECRET")
	raw = b""
	header_sig = ""
	if req:
		header_sig = req.headers.get("X-Hub-Signature-256") or req.headers.get("X-Hub-Signature") or ""
		try:
			raw = req.get_data() or b""
		except Exception:
			raw = b""
	if not verify_meta_signature(raw, header_sig, app_secret):
		frappe.throw("Invalid Meta signature", frappe.PermissionError)
	try:
		payload = req.get_json() if req else {}
	except Exception:
		payload = {}
	if not isinstance(payload, dict):
		payload = {}
	page_id = frappe.db.get_single_value("Pushesale Settings", "facebook_page_id") or ""
	page_name = frappe.db.get_single_value("Pushesale Settings", "facebook_page_name") or ""
	return handle_feed_event(payload, page_id=page_id, page_name=page_name)
