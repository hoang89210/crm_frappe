"""Phase 2 tests: Chatwoot webhook payloads -> CRM Lead (auto rollback)."""

import frappe
from frappe.tests.utils import FrappeTestCase

from pushesale.api import chatwoot


def _incoming_msg(**overrides):
	payload = {
		"event": "message_created",
		"id": 101,
		"content": "cho minh hoi gia, sdt 0912345678 nhe shop",
		"message_type": "incoming",
		"conversation": {"id": 55, "display_id": 12},
		"sender": {"id": 77, "name": "Khach Hang", "phone_number": ""},
		"account": {"id": 1},
		"inbox": {"id": 3, "name": "Facebook Page"},
	}
	payload.update(overrides)
	return payload


class TestChatwootWebhook(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_incoming_message_creates_lead(self):
		res = chatwoot.handle_event(_incoming_msg())
		self.assertTrue(res["ok"])
		lead = frappe.get_doc("CRM Lead", res["lead"])
		self.assertEqual(lead.custom_phone_e164, "+84912345678")
		self.assertEqual(lead.mobile_no, "0912345678")
		self.assertEqual(lead.source, "Chatwoot")
		self.assertEqual(lead.custom_source_detail, "Facebook Page")
		self.assertEqual(lead.custom_external_id, "chatwoot:77")
		self.assertEqual(lead.custom_chatwoot_contact_id, "77")
		self.assertEqual(lead.custom_chatwoot_conversation_id, "12")

	def test_resend_same_number_no_duplicate(self):
		first = chatwoot.handle_event(_incoming_msg())
		second = chatwoot.handle_event(_incoming_msg(content="em goi lai 0912.345.678"))
		self.assertEqual(first["lead"], second["lead"])
		n = frappe.db.count("CRM Lead", {"custom_external_id": "chatwoot:77"})
		self.assertEqual(n, 1)

	def test_contact_phone_used_when_no_number_in_text(self):
		payload = _incoming_msg(content="chao shop", sender={"id": 78, "name": "Co Sdt", "phone_number": "+84987654321"})
		res = chatwoot.handle_event(payload)
		lead = frappe.get_doc("CRM Lead", res["lead"])
		self.assertEqual(lead.custom_phone_e164, "+84987654321")

	def test_outgoing_message_skipped(self):
		res = chatwoot.handle_event(_incoming_msg(message_type="outgoing"))
		self.assertEqual(res.get("skipped"), "not-incoming")

	def test_unsupported_event_skipped(self):
		res = chatwoot.handle_event({"event": "conversation_resolved"})
		self.assertTrue(res["skipped"].startswith("unsupported-event"))

	def test_conversation_created_with_contact(self):
		payload = {
			"event": "conversation_created",
			"conversation": {"id": 60, "display_id": 20},
			"contact": {"id": 79, "name": "Moi Nhay Vao", "phone_number": ""},
			"inbox": {"id": 3, "name": "Website"},
			"account": {"id": 1},
		}
		res = chatwoot.handle_event(payload)
		lead = frappe.get_doc("CRM Lead", res["lead"])
		self.assertEqual(lead.custom_external_id, "chatwoot:79")

	def test_secret_check(self):
		old = frappe.get_site_config().get("CHATWOOT_WEBHOOK_SECRET")
		try:
			frappe.conf["CHATWOOT_WEBHOOK_SECRET"] = "s3cret-test"
			self.assertTrue(chatwoot.is_valid_secret("s3cret-test"))
			self.assertFalse(chatwoot.is_valid_secret("wrong"))
			self.assertFalse(chatwoot.is_valid_secret(""))
			self.assertFalse(chatwoot.is_valid_secret(None))
		finally:
			if old is None:
				frappe.conf.pop("CHATWOOT_WEBHOOK_SECRET", None)
			else:
				frappe.conf["CHATWOOT_WEBHOOK_SECRET"] = old
