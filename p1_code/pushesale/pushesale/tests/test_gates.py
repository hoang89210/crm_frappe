"""Phase 1 acceptance gates as regression tests (auto rollback).

Note: permission checks must use frappe.get_list (frappe.get_all skips
permission checks by design).
"""

import frappe
import frappe.client
from frappe.tests.utils import FrappeTestCase

from pushesale.api.lead import upsert_lead
from pushesale.import_leads import run_import


def _make_user(email):
	if frappe.db.exists("User", email):
		return email
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


class TestPhase1Gates(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_csv_import_sample(self):
		res1 = run_import()
		self.assertEqual(res1["created"], 3)
		self.assertEqual(res1["skipped"], 0)
		res2 = run_import()
		self.assertEqual(res2["created"], 0)
		self.assertEqual(res2["merged"], 3)
		total = frappe.db.count("CRM Lead", {"custom_external_id": ["like", "import-%"]})
		self.assertEqual(total, 3)

	def test_sales_ab_isolation(self):
		a = _make_user("gate_sales_a@example.com")
		b = _make_user("gate_sales_b@example.com")
		lead = upsert_lead({"phone": "0901212121", "first_name": "Cua A", "owner": a})

		frappe.set_user(b)
		self.assertEqual(len(frappe.get_list("CRM Lead", filters={"name": lead})), 0)
		# API layer (REST) enforces row-level read; server-side get_doc does not.
		with self.assertRaises(frappe.PermissionError):
			frappe.client.get("CRM Lead", lead)

		frappe.set_user(a)
		self.assertEqual(len(frappe.get_list("CRM Lead", filters={"name": lead})), 1)

	def test_device_isolation(self):
		a = _make_user("gate_sales_a@example.com")
		b = _make_user("gate_sales_b@example.com")
		frappe.set_user("Administrator")
		dev = frappe.get_doc(
			{
				"doctype": "Call Device",
				"device_name": "Gate May A",
				"user": a,
				"device_token": "gate-tok-a-1",
			}
		)
		dev.insert(ignore_permissions=True)

		frappe.set_user(b)
		self.assertEqual(len(frappe.get_list("Call Device", filters={"name": dev.name})), 0)

		frappe.set_user(a)
		self.assertEqual(len(frappe.get_list("Call Device", filters={"name": dev.name})), 1)
