import frappe

from pushesale.api import fb_pages
from pushesale.api.lead import upsert_lead


def _expect_throw(fn, needle):
	try:
		fn()
	except Exception as exc:
		assert needle.lower() in str(exc).lower(), str(exc)
		return
	raise AssertionError("expected throw: " + needle)


def run():
	meta = frappe.get_meta("CRM Lead")
	assert meta.has_field("custom_fb_page_id")
	assert meta.has_field("custom_fb_page_name")
	assert frappe.db.exists("DocType", "Facebook Page Channel")

	rows = fb_pages.list_pages()
	assert isinstance(rows, list), rows

	_expect_throw(lambda: fb_pages.save_page(page_url="https://facebook.com/x"), "token")
	_expect_throw(lambda: fb_pages.sync_page("khong-ton-tai"), "không thấy page")

	hooks = frappe.get_hooks("scheduler_events")
	cron = hooks.get("cron", {})
	methods = cron.get("*/10 * * * *", [])
	assert "pushesale.api.fb_pages.scheduled_sync_pages" in methods, methods

	ext = "fbtest:page:001"
	lead = upsert_lead(
		{
			"external_id": ext,
			"phone": "+84912000009",
			"name": "FB Page Test",
			"source": "Facebook Comment",
			"source_detail": "Page A",
			"raw_text": "sdt 0912000009",
			"fb_page_id": "111222333",
			"fb_page_name": "Page A",
		}
	)
	doc = frappe.get_doc("CRM Lead", lead)
	assert doc.custom_fb_page_id == "111222333", doc.custom_fb_page_id
	assert doc.custom_fb_page_name == "Page A", doc.custom_fb_page_name
	frappe.delete_doc("CRM Lead", lead, ignore_permissions=True, force=1)
	frappe.db.commit()
	print("FB_SELFTEST_OK")
