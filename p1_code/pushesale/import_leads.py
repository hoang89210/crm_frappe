"""CSV import via upsert_lead. Run: bench --site crm.local execute pushesale.import_leads.run_import."""

import csv
import os

import frappe

from pushesale.api.lead import upsert_lead


def run_import(file_path=None):
	if not file_path:
		file_path = os.path.join(os.path.dirname(__file__), "sample_leads.csv")
	created, merged, skipped = 0, 0, 0
	with open(file_path, newline="", encoding="utf-8-sig") as f:
		for row in csv.DictReader(f):
			phone = (row.get("mobile_no") or "").strip()
			if not phone:
				skipped += 1
				continue
			before = frappe.db.get_value(
				"CRM Lead", {"custom_external_id": (row.get("custom_external_id") or "").strip()}, "name"
			) if (row.get("custom_external_id") or "").strip() else None
			name = upsert_lead(
				{
					"first_name": (row.get("first_name") or "").strip(),
					"phone": phone,
					"source": (row.get("source") or "").strip() or None,
					"source_detail": (row.get("custom_source_detail") or "").strip() or None,
					"external_id": (row.get("custom_external_id") or "").strip() or None,
				}
			)
			if before and before == name:
				merged += 1
			else:
				created += 1
	return {"created": created, "merged": merged, "skipped": skipped, "file": file_path}
