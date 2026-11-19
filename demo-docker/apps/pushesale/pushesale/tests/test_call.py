"""Phase 4 tests: register/create_job/poll/disposition/skip_job (auto rollback)."""

import frappe
from frappe.tests.utils import FrappeTestCase

from pushesale.api import call as call_api
from pushesale.api.lead import upsert_lead


def _make_sales(email):
	if not frappe.db.exists("User", email):
		u = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": email.split("@")[0],
				"roles": [{"role": "Sales User"}],
				"send_welcome_email": 0,
			}
		)
		u.insert(ignore_permissions=True)
	return email


class TestCallBridge(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_register_idempotent(self):
		sale = _make_sales("call_sale_a@example.com")
		frappe.set_user(sale)
		r1 = call_api.register_device("May Test A")
		r2 = call_api.register_device("May Test A")
		self.assertEqual(r1["device_token"], r2["device_token"])
		self.assertTrue(r1["device_token"])

	def test_create_job_requires_device(self):
		sale = _make_sales("call_sale_b@example.com")
		lead = upsert_lead({"phone": "0901414141", "first_name": "No Device", "owner": sale})
		frappe.set_user(sale)
		with self.assertRaises(frappe.ValidationError):
			call_api.create_job(lead)

	def test_create_job_requires_phone(self):
		sale = _make_sales("call_sale_c@example.com")
		frappe.set_user(sale)
		call_api.register_device("May Test C")
		lead = upsert_lead({"first_name": "No Phone", "owner": sale})
		with self.assertRaises(frappe.ValidationError):
			call_api.create_job(lead)

	def test_full_flow_hen_goi_lai(self):
		sale = _make_sales("call_sale_d@example.com")
		frappe.set_user("Administrator")
		lead = upsert_lead({"phone": "0901515151", "first_name": "Full Flow", "owner": sale})
		frappe.set_user(sale)
		reg = call_api.register_device("May Test D")
		token = reg["device_token"]

		created = call_api.create_job(lead)
		self.assertEqual(created["phone"], "0901515151")

		polled = call_api.poll(device_token=token)
		self.assertEqual(polled["job"], created["job"])
		self.assertEqual(polled["status"], "Delivered")

		res = call_api.disposition(
			device_token=token,
			job=created["job"],
			ket_qua="Hen goi lai",
			ngay_hen="2030-05-06 09:00:00",
		)
		self.assertTrue(res["ok"])
		self.assertEqual(res["care_status"], "Hẹn gọi lại")
		updated = frappe.get_doc("CRM Lead", lead)
		self.assertEqual(updated.custom_care_status, "Hẹn gọi lại")
		self.assertIsNotNone(updated.custom_next_followup)
		job = frappe.get_doc("Call Job", created["job"])
		self.assertEqual(job.status, "Closed")
		self.assertEqual(job.call_log, res["call_log"])

	def test_disposition_wrong_device_token(self):
		sale = _make_sales("call_sale_e@example.com")
		other = _make_sales("call_sale_f@example.com")
		frappe.set_user("Administrator")
		lead = upsert_lead({"phone": "0901616161", "first_name": "Wrong Tok", "owner": sale})
		frappe.set_user(sale)
		reg = call_api.register_device("May Test E")
		created = call_api.create_job(lead)
		frappe.set_user(other)
		other_reg = call_api.register_device("May Test F")
		with self.assertRaises(frappe.PermissionError):
			call_api.disposition(
				device_token=other_reg["device_token"],
				job=created["job"],
				ket_qua="Chot",
			)

	def test_skip_job_no_call_log(self):
		sale = _make_sales("call_sale_g@example.com")
		frappe.set_user("Administrator")
		lead = upsert_lead({"phone": "0901717171", "first_name": "Skip Me", "owner": sale})
		frappe.set_user(sale)
		reg = call_api.register_device("May Test G")
		created = call_api.create_job(lead)
		res = call_api.skip_job(device_token=reg["device_token"], job=created["job"])
		self.assertEqual(res["status"], "Expired")
		self.assertEqual(frappe.db.count("Call Log", {"job": created["job"]}), 0)
		updated = frappe.get_doc("CRM Lead", lead)
		self.assertEqual(updated.custom_care_status, "Mới")

	def test_poll_empty(self):
		sale = _make_sales("call_sale_h@example.com")
		frappe.set_user(sale)
		reg = call_api.register_device("May Test H")
		res = call_api.poll(device_token=reg["device_token"])
		self.assertIsNone(res["job"])

	def test_poll_unknown_token(self):
		with self.assertRaises(frappe.PermissionError):
			call_api.poll(device_token="nope-wrong-token")

	def test_cannot_call_others_lead(self):
		owner = _make_sales("call_sale_i@example.com")
		intruder = _make_sales("call_sale_j@example.com")
		frappe.set_user("Administrator")
		lead = upsert_lead({"phone": "0901919191", "first_name": "Cua I", "owner": owner})
		frappe.set_user(intruder)
		call_api.register_device("May Test J")
		with self.assertRaises(frappe.PermissionError):
			call_api.create_job(lead)

	def test_marketing_cannot_call(self):
		email = "call_mkt@example.com"
		if not frappe.db.exists("User", email):
			u = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": "mkt",
					"roles": [{"role": "Marketing"}],
					"send_welcome_email": 0,
				}
			)
			u.insert(ignore_permissions=True)
		frappe.set_user(email)
		with self.assertRaises(frappe.PermissionError):
			call_api.register_device("May Mkt")
		frappe.set_user("Administrator")
		lead = upsert_lead({"phone": "0901818181", "first_name": "Mkt Lead"})
		frappe.set_user(email)
		with self.assertRaises(frappe.PermissionError):
			call_api.create_job(lead)
