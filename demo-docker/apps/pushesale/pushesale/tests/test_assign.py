"""Tests for manual reassignment (auto rollback)."""

import frappe
from frappe.tests.utils import FrappeTestCase

from pushesale.api import assign as assign_api
from pushesale.api import call as call_api
from pushesale.api.lead import upsert_lead


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


class TestReassign(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_manager_reassign_by_phone(self):
		a = _make_user("rs_a@example.com", "Sales User")
		b = _make_user("rs_b@example.com", "Sales User")
		mgr = _make_user("rs_mgr@example.com", "Sales Manager")
		lead = upsert_lead({"phone": "0902020202", "first_name": "Chuyen", "owner": a})

		frappe.set_user(mgr)
		res = assign_api.reassign_lead(phone="0902.020.202", new_owner=b, ly_do="chia lai")
		self.assertTrue(res["ok"])
		self.assertEqual(res["old_owner"], a)
		self.assertEqual(res["new_owner"], b)
		self.assertEqual(frappe.db.get_value("CRM Lead", lead, "lead_owner"), b)

		comments = frappe.get_all(
			"Comment",
			filters={"reference_doctype": "CRM Lead", "reference_name": lead},
			fields=["content"],
		)
		self.assertTrue(any("Chuyển lead" in (c.content or "") for c in comments))

	def test_sales_cannot_reassign(self):
		a = _make_user("rs_c@example.com", "Sales User")
		b = _make_user("rs_d@example.com", "Sales User")
		lead = upsert_lead({"phone": "0902121212", "first_name": "Cuop", "owner": a})
		frappe.set_user(a)
		with self.assertRaises(frappe.PermissionError):
			assign_api.reassign_lead(lead=lead, new_owner=b)

	def test_old_owner_loses_call_new_owner_gains(self):
		a = _make_user("rs_e@example.com", "Sales User")
		b = _make_user("rs_f@example.com", "Sales User")
		mgr = _make_user("rs_mgr2@example.com", "Sales Manager")
		lead = upsert_lead({"phone": "0902323232", "first_name": "Doi May", "owner": a})

		frappe.set_user(mgr)
		assign_api.reassign_lead(lead=lead, new_owner=b)

		frappe.set_user(a)
		call_api.register_device("May RS E")
		with self.assertRaises(frappe.PermissionError):
			call_api.create_job(lead)

		frappe.set_user(b)
		call_api.register_device("May RS F")
		job = call_api.create_job(lead)
		self.assertTrue(job["job"])

	def test_unknown_phone(self):
		mgr = _make_user("rs_mgr3@example.com", "Sales Manager")
		b = _make_user("rs_g@example.com", "Sales User")
		frappe.set_user(mgr)
		with self.assertRaises(frappe.ValidationError):
			assign_api.reassign_lead(phone="0902999999", new_owner=b)

	def test_same_owner_unchanged(self):
		a = _make_user("rs_h@example.com", "Sales User")
		mgr = _make_user("rs_mgr4@example.com", "Sales Manager")
		lead = upsert_lead({"phone": "0902424242", "first_name": "Giu Nguyen", "owner": a})
		frappe.set_user(mgr)
		res = assign_api.reassign_lead(lead=lead, new_owner=a)
		self.assertTrue(res.get("unchanged"))

	def test_target_must_be_sales(self):
		mgr = _make_user("rs_mgr5@example.com", "Sales Manager")
		mkt = _make_user("rs_mkt@example.com", "Marketing")
		a = _make_user("rs_i@example.com", "Sales User")
		lead = upsert_lead({"phone": "0902525252", "first_name": "Dung Mkt", "owner": a})
		frappe.set_user(mgr)
		with self.assertRaises(frappe.ValidationError):
			assign_api.reassign_lead(lead=lead, new_owner=mkt)
