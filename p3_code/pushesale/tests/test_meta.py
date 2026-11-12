"""Phase 3: Facebook comment -> lead + Meta webhook (auto rollback)."""

import hashlib
import hmac

import frappe
from frappe.tests.utils import FrappeTestCase

from pushesale.api import http as http_api
from pushesale.api import meta
from pushesale.api import settings as settings_api


class TestMetaComments(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self._orig_http = http_api.http_json

	def tearDown(self):
		http_api.http_json = self._orig_http
		frappe.set_user("Administrator")

	def test_parse_page_url(self):
		self.assertEqual(meta.parse_facebook_page_ref("https://www.facebook.com/shopabc"), "shopabc")
		self.assertEqual(meta.parse_facebook_page_ref("facebook.com/pages/Shop/123456"), "123456")
		self.assertEqual(
			meta.parse_facebook_page_ref("https://facebook.com/profile.php?id=999"), "999"
		)
		self.assertEqual(meta.parse_facebook_page_ref("111222"), "111222")

	def test_comment_with_phone_creates_lead(self):
		leads = meta.process_comment(
			{
				"id": "c1",
				"message": "goi minh 0912.111.001 nhe",
				"from": {"name": "Anh A", "id": "u1"},
			},
			page_id="PAGE1",
			page_name="Shop ABC",
		)
		self.assertEqual(len(leads), 1)
		lead = frappe.get_doc("CRM Lead", leads[0])
		self.assertEqual(lead.custom_phone_e164, "+84912111001")
		self.assertEqual(lead.mobile_no, "0912111001")
		self.assertEqual(lead.source, "Facebook Comment")
		self.assertEqual(lead.custom_source_detail, "Shop ABC")
		self.assertEqual(lead.custom_external_id, "fbcomment:c1:+84912111001")
		self.assertEqual(lead.first_name, "Anh")

	def test_comment_without_phone_skipped(self):
		leads = meta.process_comment({"id": "c2", "message": "gia bao nhieu shop"})
		self.assertEqual(leads, [])
		n = frappe.db.count("CRM Lead", {"custom_external_id": ["like", "fbcomment:c2%"]})
		self.assertEqual(n, 0)

	def test_duplicate_comment_same_lead(self):
		payload = {
			"id": "c3",
			"message": "sdt 0912111002",
			"from": {"name": "Be B"},
		}
		a = meta.process_comment(payload)[0]
		b = meta.process_comment(payload)[0]
		self.assertEqual(a, b)
		n = frappe.db.count("CRM Lead", {"custom_external_id": "fbcomment:c3:+84912111002"})
		self.assertEqual(n, 1)

	def test_two_phones_two_leads(self):
		leads = meta.process_comment(
			{
				"id": "c4",
				"message": "lh 0912111003 hoac 0987111004",
				"from": {"name": "Chi C"},
			}
		)
		self.assertEqual(len(leads), 2)
		self.assertNotEqual(leads[0], leads[1])

	def test_price_not_phone(self):
		leads = meta.process_comment({"id": "c5", "message": "gia chi 150.000 dong"})
		self.assertEqual(leads, [])

	def test_webhook_payload_creates_lead(self):
		payload = {
			"object": "page",
			"entry": [
				{
					"id": "PAGE1",
					"changes": [
						{
							"field": "feed",
							"value": {
								"item": "comment",
								"comment_id": "123_456",
								"post_id": "123_789",
								"message": "goi minh 0912.111.005 nhe",
								"from": {"name": "Anh Webhook", "id": "111"},
							},
						}
					],
				}
			],
		}
		res = meta.handle_feed_event(payload, page_name="Shop")
		self.assertEqual(len(res["leads"]), 1)
		lead = frappe.get_doc("CRM Lead", res["leads"][0])
		self.assertEqual(lead.custom_external_id, "fbcomment:123_456:+84912111005")

	def test_webhook_no_phone_skipped(self):
		payload = {
			"object": "page",
			"entry": [
				{
					"id": "PAGE1",
					"changes": [
						{
							"field": "feed",
							"value": {
								"item": "comment",
								"comment_id": "x_y",
								"message": "hello shop",
								"from": {"name": "Z"},
							},
						}
					],
				}
			],
		}
		res = meta.handle_feed_event(payload)
		self.assertEqual(res["leads"], [])
		self.assertEqual(res["skipped_no_phone"], 1)

	def test_verify_subscription(self):
		ch = meta.handle_verify("subscribe", "tok", "4242", "tok")
		self.assertEqual(ch, "4242")
		with self.assertRaises(frappe.PermissionError):
			meta.handle_verify("subscribe", "wrong", "4242", "tok")

	def test_signature(self):
		body = b'{"object":"page"}'
		secret = "app-secret"
		sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
		self.assertTrue(meta.verify_meta_signature(body, sig, secret))
		self.assertFalse(meta.verify_meta_signature(body, sig, "other"))
		self.assertFalse(meta.verify_meta_signature(body, "", secret))

	def test_invalid_token(self):
		def fake(method, url, headers=None, params=None, json_body=None, timeout=15):
			return 400, {"error": {"message": "Invalid OAuth access token."}}

		http_api.http_json = fake
		settings_api.save_settings(facebook_access_token="bad-token")
		with self.assertRaises(frappe.ValidationError):
			meta.test_connection(facebook_access_token="bad-token")

	def test_sync_recent_mock(self):
		settings_api.save_settings(
			facebook_page_url="https://facebook.com/shopabc",
			facebook_access_token="page-token-0001",
			facebook_sync_enabled=1,
		)
		calls = {"n": 0}

		def fake(method, url, headers=None, params=None, json_body=None, timeout=15):
			calls["n"] += 1
			if "/feed" in url:
				return 200, {
					"data": [
						{
							"id": "111_p1",
							"comments": {
								"data": [
									{
										"id": "c10",
										"message": "goi minh 0912.000.001 nhe",
										"from": {"name": "Anh A"},
									},
									{
										"id": "c11",
										"message": "gia bao nhieu",
										"from": {"name": "Be B"},
									},
									{
										"id": "c12",
										"message": "lh 0912000002 hoac 0987000003",
										"from": {"name": "Chi C"},
									},
								]
							},
							"paging": {"next": "https://graph.facebook.com/never-follow"},
						}
					],
					"paging": {"next": "https://graph.facebook.com/never-follow"},
				}
			return 200, {"id": "111", "name": "Shop ABC"}

		http_api.http_json = fake
		res = meta.sync_recent()
		self.assertTrue(res["ok"])
		self.assertEqual(res["created"], 3)
		self.assertEqual(res["skipped_no_phone"], 1)
		self.assertEqual(res["posts"], 1)
		self.assertEqual(res["comments"], 3)
		self.assertEqual(res["page_id"], "111")
		self.assertLessEqual(calls["n"], 3)
		self.assertTrue(
			frappe.db.exists("CRM Lead", {"custom_external_id": "fbcomment:c10:+84912000001"})
		)
		self.assertTrue(
			frappe.db.exists("CRM Lead", {"custom_external_id": "fbcomment:c12:+84987000003"})
		)
		self.assertFalse(
			frappe.db.exists("CRM Lead", {"custom_external_id": ["like", "fbcomment:c11%"]})
		)

	def test_scheduled_skipped_without_token(self):
		settings_api.save_settings(facebook_sync_enabled=1, facebook_access_token="")
		doc = settings_api.get_settings_doc()
		doc.facebook_access_token = ""
		doc.facebook_sync_enabled = 1
		doc.save(ignore_permissions=True)
		# If a previous test left a token in this transaction, scheduled may run.
		# Disabled path:
		settings_api.save_settings(facebook_sync_enabled=0)
		res = meta.scheduled_sync()
		self.assertEqual(res.get("skipped"), "disabled")
