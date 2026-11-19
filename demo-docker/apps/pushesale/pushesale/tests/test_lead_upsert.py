import uuid

import frappe
from frappe.tests.utils import FrappeTestCase

from pushesale.api.care import apply_call_result
from pushesale.api.lead import upsert_lead


def _uid():
	return uuid.uuid4().hex[:8]


class TestLeadUpsert(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_same_phone_merges_to_one_lead(self):
		phone = "0901111222"
		n1 = upsert_lead(
			{
				"phone": phone,
				"first_name": "An",
				"source": "Website",
				"external_id": f"test-ext-{_uid()}",
			}
		)
		n2 = upsert_lead({"phone": "0901.111.222", "first_name": "An Khac"})
		n3 = upsert_lead({"phone": "+84901111222", "first_name": "An Nua"})
		self.assertEqual(n1, n2)
		self.assertEqual(n1, n3)
		lead = frappe.get_doc("CRM Lead", n1)
		self.assertEqual(lead.custom_phone_e164, "+84901111222")
		self.assertEqual(lead.mobile_no, "0901111222")

	def test_care_status_not_overwritten(self):
		phone = "0903333444"
		name = upsert_lead({"phone": phone, "first_name": "Binh"})
		lead = frappe.get_doc("CRM Lead", name)
		lead.custom_care_status = "Chốt"
		lead.save(ignore_permissions=True)
		n2 = upsert_lead({"phone": phone, "first_name": "Binh Moi"})
		self.assertEqual(name, n2)
		self.assertEqual(
			frappe.db.get_value("CRM Lead", name, "custom_care_status"), "Chốt"
		)

	def test_churn_disposition_keeps_doc(self):
		name = upsert_lead({"phone": "0905555666", "first_name": "Churn Case"})
		log = frappe.get_doc(
			{
				"doctype": "Call Log",
				"lead": name,
				"phone": "0905555666",
				"sale": "Administrator",
			}
		)
		log.insert(ignore_permissions=True)
		log.ket_qua = "Churn"
		log.save(ignore_permissions=True)
		lead = frappe.get_doc("CRM Lead", name)
		self.assertEqual(lead.custom_care_status, "Churn")
		self.assertEqual(lead.custom_care_count, 1)
		self.assertTrue(frappe.db.exists("CRM Lead", name))

	def test_hen_goi_lai_sets_followup(self):
		name = upsert_lead({"phone": "0907777888", "first_name": "Hen Case"})
		log = frappe.get_doc(
			{
				"doctype": "Call Log",
				"lead": name,
				"phone": "0907777888",
				"sale": "Administrator",
				"ngay_hen": "2030-01-02 10:00:00",
			}
		)
		log.insert(ignore_permissions=True)
		log.ket_qua = "Hen goi lai"
		log.save(ignore_permissions=True)
		lead = frappe.get_doc("CRM Lead", name)
		self.assertEqual(lead.custom_care_status, "Hẹn gọi lại")
		self.assertIsNotNone(lead.custom_next_followup)

	def test_insert_without_result_changes_nothing(self):
		name = upsert_lead({"phone": "0902222333", "first_name": "No Result Case"})
		log = frappe.get_doc(
			{
				"doctype": "Call Log",
				"lead": name,
				"phone": "0902222333",
				"sale": "Administrator",
			}
		)
		log.insert(ignore_permissions=True)
		lead = frappe.get_doc("CRM Lead", name)
		self.assertEqual(lead.custom_care_status, "Mới")
		self.assertEqual(lead.custom_care_count, 0)

	def test_apply_call_result_direct(self):
		name = upsert_lead({"phone": "0909999000", "first_name": "Direct Case"})
		log = frappe.get_doc(
			{
				"doctype": "Call Log",
				"lead": name,
				"phone": "0909999000",
				"sale": "Administrator",
				"ket_qua": "Can cham tiep",
			}
		)
		log.insert(ignore_permissions=True)
		# ket_qua filled at insert: on_update runs with no before -> applies once.
		# Direct call afterwards must be a no-op (already recorded).
		apply_call_result(log.name)
		lead = frappe.get_doc("CRM Lead", name)
		self.assertEqual(lead.custom_care_count, 1)
		self.assertEqual(lead.custom_care_status, "Cần chăm tiếp")
