"""Multi-page Facebook comment sync.

Each `Facebook Page Channel` stores its own page id + Page Access Token.
Scheduler syncs every enabled page; webhook/legacy single-page settings keep
working through pushesale.api.meta.
"""

import frappe

from pushesale.api.lead import upsert_lead
from pushesale.api.meta import FEED_COMMENT_LIMIT, FEED_POST_LIMIT, _graph_error, graph_get, resolve_page
from pushesale.api.settings import require_settings_role
from pushesale.phone import extract_vn_phones

DOCTYPE = "Facebook Page Channel"


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


def _page_token(name):
	if not name or not frappe.db.exists(DOCTYPE, name):
		return ""
	try:
		return frappe.get_doc(DOCTYPE, name).get_password("access_token") or ""
	except Exception:
		return ""


def _as_dict(doc):
	return {
		"name": doc.name,
		"page_name": doc.page_name,
		"page_id": doc.page_id,
		"page_url": doc.page_url or "",
		"sync_enabled": int(doc.sync_enabled or 0),
		"last_sync": str(doc.last_sync or ""),
		"last_result": doc.last_result or "",
	}


@frappe.whitelist()
def list_pages():
	require_settings_role()
	docs = frappe.get_all(
		DOCTYPE,
		fields=["name", "page_name", "page_id", "page_url", "sync_enabled", "last_sync", "last_result"],
		order_by="page_name asc",
	)
	for row in docs:
		token = _page_token(row["name"])
		row["has_token"] = 1 if token else 0
		row["token_hint"] = (token[-4:] if token else "")
	return docs


@frappe.whitelist()
def test_page(page_url=None, access_token=None):
	require_settings_role()
	token = _text(access_token)
	if not token or token.startswith("****"):
		frappe.throw("Nhập Page Access Token để kiểm tra.", frappe.ValidationError)
	info = resolve_page(token, _text(page_url))
	return {"ok": True, "page_id": info["id"], "page_name": info["name"]}


@frappe.whitelist()
def save_page(name=None, page_name=None, page_url=None, access_token=None, sync_enabled=1):
	require_settings_role()
	name = _text(name)
	page_url = _text(page_url)
	existing = frappe.get_doc(DOCTYPE, name) if name and frappe.db.exists(DOCTYPE, name) else None
	token = _text(access_token)
	if not token or token.startswith("****"):
		token = _page_token(name)
	if not token:
		frappe.throw("Cần Page Access Token.", frappe.ValidationError)
	info = resolve_page(token, page_url or (existing.page_url if existing else ""))
	label = _text(page_name) or info["name"] or info["id"]
	if existing:
		doc = existing
		doc.page_name = label
		doc.page_id = info["id"]
		doc.page_url = page_url or doc.page_url
		doc.sync_enabled = _flag(sync_enabled)
		doc.access_token = token
		doc.save(ignore_permissions=True)
	else:
		dup = frappe.db.get_value(DOCTYPE, {"page_id": info["id"]}, "name")
		if dup:
			doc = frappe.get_doc(DOCTYPE, dup)
			doc.page_name = label
			doc.page_url = page_url or doc.page_url
			doc.sync_enabled = _flag(sync_enabled)
			doc.access_token = token
			doc.save(ignore_permissions=True)
		else:
			if frappe.db.exists(DOCTYPE, label):
				label = f"{label} ({info['id']})"
			doc = frappe.get_doc(
				{
					"doctype": DOCTYPE,
					"page_name": label,
					"page_id": info["id"],
					"page_url": page_url,
					"sync_enabled": _flag(sync_enabled),
					"access_token": token,
				}
			).insert(ignore_permissions=True)
	frappe.db.commit()
	return _as_dict(doc)


@frappe.whitelist()
def delete_page(name):
	require_settings_role()
	name = _text(name)
	if not name or not frappe.db.exists(DOCTYPE, name):
		frappe.throw("Không thấy Page")
	frappe.delete_doc(DOCTYPE, name, ignore_permissions=True, force=1)
	frappe.db.commit()
	return {"ok": 1}


def _upsert_comment(comment, page, stats):
	comment = comment or {}
	message = comment.get("message") or ""
	phones = extract_vn_phones(message)
	if not phones:
		stats["skipped_no_phone"] += 1
		return
	comment_id = str(comment.get("id") or comment.get("comment_id") or "")
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
				"source_detail": page["page_name"],
				"raw_text": message,
				"fb_page_id": page["page_id"],
				"fb_page_name": page["page_name"],
			}
		)
		stats["merged" if existed else "created"] += 1


def _sync_doc(doc):
	token = _page_token(doc.name)
	if not token:
		return {"ok": False, "page": doc.page_name, "error": "Chưa có access token"}
	page = _as_dict(doc)
	if not page["page_id"]:
		info = resolve_page(token, page["page_url"])
		doc.page_id = info["id"]
		doc.page_name = doc.page_name or info["name"]
		doc.save(ignore_permissions=True)
		page = _as_dict(doc)
	since = None
	if doc.last_sync:
		try:
			since = int(frappe.utils.get_datetime(doc.last_sync).timestamp())
		except Exception:
			since = None
	params = {
		"fields": f"id,created_time,comments.limit({FEED_COMMENT_LIMIT}){{id,message,from,created_time}}",
		"limit": FEED_POST_LIMIT,
	}
	if since:
		params["since"] = since
	status, data = graph_get(f"{page['page_id']}/feed", token, params)
	if status != 200:
		doc.last_result = _graph_error(data)
		doc.save(ignore_permissions=True)
		return {"ok": False, "page": page["page_name"], "error": doc.last_result}
	stats = {"created": 0, "merged": 0, "skipped_no_phone": 0, "posts": 0, "comments": 0}
	for post in (data or {}).get("data") or []:
		stats["posts"] += 1
		for comment in ((post or {}).get("comments") or {}).get("data") or []:
			stats["comments"] += 1
			_upsert_comment(comment, page, stats)
	summary = (
		f"{page['page_name']}: {stats['created']} lead mới, {stats['merged']} trùng, "
		f"{stats['skipped_no_phone']} bỏ (không SĐT), {stats['posts']} bài / {stats['comments']} comment."
	)
	doc.last_sync = frappe.utils.now_datetime()
	doc.last_result = summary
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "page": page["page_name"], "result": summary, **stats}


@frappe.whitelist()
def sync_page(name):
	require_settings_role()
	name = _text(name)
	if not name or not frappe.db.exists(DOCTYPE, name):
		frappe.throw("Không thấy Page")
	return _sync_doc(frappe.get_doc(DOCTYPE, name))


@frappe.whitelist()
def sync_all():
	require_settings_role()
	return _sync_all()


def _sync_all():
	pages = frappe.get_all(DOCTYPE, filters={"sync_enabled": 1}, pluck="name")
	results = []
	for name in pages:
		try:
			results.append(_sync_doc(frappe.get_doc(DOCTYPE, name)))
		except Exception as exc:
			results.append({"ok": False, "page": name, "error": str(exc)[:180]})
	frappe.db.commit()
	ok = sum(1 for r in results if r.get("ok"))
	return {
		"ok": True,
		"pages": len(results),
		"synced": ok,
		"result": f"Đồng bộ {ok}/{len(results)} Page.",
		"details": results,
	}


def scheduled_sync_pages():
	try:
		if not frappe.db.count(DOCTYPE):
			return {"ok": True, "skipped": "no-pages"}
		return _sync_all()
	except Exception:
		frappe.log_error("pushesale fb_pages scheduled_sync failed")
		return {"ok": False}
