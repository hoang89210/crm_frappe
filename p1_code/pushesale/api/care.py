"""Apply a Call Log result to its CRM Lead.

Runs only when `ket_qua` was just filled (before: empty, now: set).
Rules (plan 3.5):
- Every result: care_count += 1, last_call_result = ket_qua, log.lan_cham = new count,
  log.trang_thai_cuoc = 'Da tra ket qua'.
- Khong nghe: consecutive no-answer >= 5 -> 'Khong nghe nhieu',
  else 'Can cham tiep', next = now + 4h.
- Thue bao (plan silent): same as Khong nghe but next = now + 1 day.
- Ban goi lai: 'Can cham tiep', next + 2h.
- Can cham tiep: 'Can cham tiep', next + 1 day.
- Hen goi lai: 'Hen goi lai', next = ngay_hen.
- Chot -> 'Chot'. Churn -> 'Churn'. Never delete the lead.
"""

import frappe
from frappe.utils import add_to_date, get_datetime, now_datetime

CARE_NEW = "Mới"
CARE_WORKING = "Cần chăm tiếp"
CARE_CALLBACK = "Hẹn gọi lại"
CARE_WON = "Chốt"
CARE_LOST = "Churn"
CARE_NOANSWER = "Không nghe nhiều"

NO_ANSWER_LIMIT = 5


def _consecutive_no_answer(lead_name, exclude_log=None):
	logs = frappe.get_all(
		"Call Log",
		filters={"lead": lead_name},
		fields=["name", "ket_qua"],
		order_by="creation desc",
		limit=50,
	)
	count = 0
	for log in logs:
		if exclude_log and log.name == exclude_log:
			continue
		if log.ket_qua == "Khong nghe":
			count += 1
		elif not log.ket_qua:
			continue
		else:
			break
	return count


def apply_call_result(call_log):
	"""Apply result of a Call Log doc to its lead. Returns lead name or None."""
	if isinstance(call_log, str):
		call_log = frappe.get_doc("Call Log", call_log)
	if not call_log.get("ket_qua") or not call_log.get("lead"):
		return None
	if call_log.get("lan_cham"):
		return None  # already counted, do not recount

	before = call_log.get_doc_before_save()
	if before and before.get("ket_qua"):
		return None  # result was already recorded before, do not recount

	lead = frappe.get_doc("CRM Lead", call_log.lead)
	ket_qua = call_log.ket_qua
	now = now_datetime()

	lead.custom_care_count = (lead.custom_care_count or 0) + 1
	lead.custom_last_call_result = ket_qua

	if ket_qua == "Khong nghe":
		streak = _consecutive_no_answer(lead.name, exclude_log=call_log.name) + 1
		if streak >= NO_ANSWER_LIMIT:
			lead.custom_care_status = CARE_NOANSWER
			lead.custom_next_followup = None
		else:
			lead.custom_care_status = CARE_WORKING
			lead.custom_next_followup = add_to_date(now, hours=4)
	elif ket_qua == "Thue bao":
		lead.custom_care_status = CARE_WORKING
		lead.custom_next_followup = add_to_date(now, days=1)
	elif ket_qua == "Ban goi lai":
		lead.custom_care_status = CARE_WORKING
		lead.custom_next_followup = add_to_date(now, hours=2)
	elif ket_qua == "Can cham tiep":
		lead.custom_care_status = CARE_WORKING
		lead.custom_next_followup = add_to_date(now, days=1)
	elif ket_qua == "Hen goi lai":
		lead.custom_care_status = CARE_CALLBACK
		lead.custom_next_followup = get_datetime(call_log.ngay_hen) if call_log.ngay_hen else None
	elif ket_qua == "Chot":
		lead.custom_care_status = CARE_WON
		lead.custom_next_followup = None
	elif ket_qua == "Churn":
		lead.custom_care_status = CARE_LOST
		lead.custom_next_followup = None

	lead.save(ignore_permissions=True)

	frappe.db.set_value(
		"Call Log",
		call_log.name,
		{
			"lan_cham": lead.custom_care_count,
			"trang_thai_cuoc": "Da tra ket qua",
		},
		update_modified=False,
	)
	return lead.name
