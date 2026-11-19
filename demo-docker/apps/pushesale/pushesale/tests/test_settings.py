"""Settings screen + Chatwoot sync (auto rollback)."""

import frappe
from frappe.tests.utils import FrappeTestCase

from pushesale.api import chatwoot
from pushesale.api import http as http_api
from pushesale.api import settings as settings_api


def _make_user(email, role):
	if not frappe.db.exists("User", email):
		u = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": email.split("@")[0],
				"roles": [{"role": role}],
				"send_welcome_email": 0,
			}
		)
		u.insert(ignore_permissions=True)
	return email


class TestPushesaleSettings(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self._orig_http = http_api.http_json

	def tearDown(self):
		http_api.http_json = self._orig_http
		frappe.set_user("Administrator")

	def test_save_masks_token(self):
		res = settings_api.save_settings(
			chatwoot_url="http://chatwoot.test",
			chatwoot_account_id="1",
			chatwoot_api_token="tok-abcdef1234",
			chatwoot_webhook_secret="s3cret-live",
		)
		self.assertEqual(res["chatwoot_url"], "http://chatwoot.test")
		self.assertTrue(res["chatwoot_api_token"].startswith("****"))
		self.assertNotIn("tok-abcdef1234", res["chatwoot_api_token"])
		self.assertEqual(res["chatwoot_api_token"][-4:], "1234")
		self.assertTrue(chatwoot.is_valid_secret("s3cret-live"))

	def test_keep_masked_token(self):
		settings_api.save_settings(chatwoot_api_token="keep-me-9999")
		settings_api.save_settings(chatwoot_api_token="****9999", chatwoot_url="http://x")
		got = settings_api.get_password_field("chatwoot_api_token")
		self.assertEqual(got, "keep-me-9999")

	def test_sales_cannot_save(self):
		sale = _make_user("set_sale@example.com", "Sales User")
		frappe.set_user(sale)
		with self.assertRaises(frappe.PermissionError):
			settings_api.save_settings(chatwoot_url="http://nope")

	def test_marketing_can_get(self):
		mkt = _make_user("set_mkt@example.com", "Marketing")
		frappe.set_user(mkt)
		res = settings_api.get_settings()
		self.assertIn("chatwoot_url", res)
		self.assertIn("facebook_page_url", res)

	def test_chatwoot_test_connection_mock(self):
		def fake(method, url, headers=None, params=None, json_body=None, timeout=15):
			if url.endswith("/profile"):
				return 200, {"name": "Agent Bot", "email": "bot@x"}
			return 404, {"error": "no"}

		http_api.http_json = fake
		res = chatwoot.test_connection(
			chatwoot_url="http://cw.test",
			chatwoot_api_token="cw-token",
			chatwoot_account_id="9",
		)
		self.assertTrue(res["ok"])
		self.assertEqual(res["name"], "Agent Bot")

	def test_chatwoot_sync_inbox_mock(self):
		settings_api.save_settings(
			chatwoot_url="http://cw.test",
			chatwoot_account_id="1",
			chatwoot_api_token="cw-token",
		)
		calls = {"n": 0}

		def fake(method, url, headers=None, params=None, json_body=None, timeout=15):
			calls["n"] += 1
			page = int((params or {}).get("page") or 1)
			if page == 1:
				return 200, {
					"payload": [
						{"id": 501, "name": "Khach Inbox", "phone_number": "0912888777"},
						{"id": 502, "name": "Khong So", "phone_number": ""},
					]
				}
			return 200, {"payload": []}

		http_api.http_json = fake
		res = chatwoot.sync_inbox()
		self.assertTrue(res["ok"])
		self.assertEqual(res["created"], 1)
		self.assertEqual(res["skipped_no_phone"], 1)
		lead = frappe.db.get_value("CRM Lead", {"custom_external_id": "chatwoot:501"}, "name")
		self.assertTrue(lead)
		self.assertEqual(
			frappe.db.get_value("CRM Lead", lead, "custom_phone_e164"), "+84912888777"
		)

	def test_chatwoot_sync_stops_after_page_limit(self):
		settings_api.save_settings(
			chatwoot_url="http://cw.test",
			chatwoot_account_id="1",
			chatwoot_api_token="cw-token",
		)
		calls = {"n": 0}

		def fake(method, url, headers=None, params=None, json_body=None, timeout=15):
			calls["n"] += 1
			return 200, {
				"payload": [
					{"id": 600 + calls["n"], "name": "X", "phone_number": "0901111111"}
					for _ in range(10)
				]
			}

		http_api.http_json = fake
		chatwoot.sync_inbox()
		self.assertEqual(calls["n"], chatwoot.CONTACTS_PAGE_LIMIT)

	def test_scheduled_skipped_when_disabled(self):
		settings_api.save_settings(chatwoot_sync_enabled=0)
		res = chatwoot.scheduled_sync()
		self.assertEqual(res.get("skipped"), "disabled")
