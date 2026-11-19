"""SIM-call bridge API (Phase 4).

Flow: CRM --create_job--> Call Job (Queued) --poll--> PWA/Android dialer
--disposition--> Call Log --> lead care status (via Call Log on_update hook).

Auth:
- create_job / register_device: logged-in user (Sales User+).
- poll / disposition / skip_job: device_token (guest allowed, token is the secret).
"""

import secrets

import frappe
from frappe.utils import add_to_date, now_datetime

JOB_TTL_MINUTES = 3

RESULTS = [
	"Khong nghe",
	"Thue bao",
	"Ban goi lai",
	"Can cham tiep",
	"Hen goi lai",
	"Chot",
	"Churn",
]

# Marketing / Bridge / Guest may not trigger SIM calls.
CALLER_ROLES = {"System Manager", "Sales Manager", "Sales User"}


def _require_caller_role(user):
	if user == "Administrator":
		return
	if not (set(frappe.get_roles(user)) & CALLER_ROLES):
		frappe.throw("Vai trò này không được gọi (chỉ Sales).", frappe.PermissionError)


def _get_device_by_token(device_token):
	if not device_token:
		return None
	name = frappe.db.get_value("Call Device", {"device_token": device_token}, "name")
	if not name:
		return None
	return frappe.get_doc("Call Device", name)


def _expire_stale_jobs(device_name):
	"""Mark past-expiry Queued/Delivered jobs Expired. Returns count."""
	now = now_datetime()
	stale = frappe.get_all(
		"Call Job",
		filters={
			"device": device_name,
			"status": ["in", ["Queued", "Delivered"]],
			"expires_on": ["<", now],
		},
		pluck="name",
	)
	for job_name in stale:
		frappe.db.set_value("Call Job", job_name, "status", "Expired")
	return len(stale)


@frappe.whitelist()
def register_device(device_name):
	"""Get-or-create this user's Call Device. Returns device_token (paste into PWA/app).

	Idempotent: same user + device_name returns the existing token.
	"""
	user = frappe.session.user
	if user in ("Guest", None):
		frappe.throw("Login required", frappe.PermissionError)
	_require_caller_role(user)
	device_name = (device_name or "").strip()
	if not device_name:
		frappe.throw("device_name is required")
	existing = frappe.db.get_value(
		"Call Device", {"user": user, "device_name": device_name}, "name"
	)
	if existing:
		doc = frappe.get_doc("Call Device", existing)
		if not doc.active:
			doc.active = 1
			doc.save(ignore_permissions=True)
		return {"device": doc.name, "device_token": doc.device_token}
	doc = frappe.get_doc(
		{
			"doctype": "Call Device",
			"device_name": device_name,
			"user": user,
			"device_token": secrets.token_urlsafe(24),
			"active": 1,
		}
	)
	doc.insert()
	return {"device": doc.name, "device_token": doc.device_token}


@frappe.whitelist()
def create_job(lead):
	"""Sale presses Goi on a CRM Lead. Creates a Queued Call Job for their device."""
	user = frappe.session.user
	if user in ("Guest", None):
		frappe.throw("Login required", frappe.PermissionError)
	_require_caller_role(user)
	if not frappe.db.exists("CRM Lead", lead):
		frappe.throw(f"Lead {lead} not found")
	# NOTE: server-side get_doc skips row-level checks, so enforce explicitly.
	if not frappe.has_permission("CRM Lead", "read", lead):
		frappe.throw("Bạn không có quyền gọi lead này.", frappe.PermissionError)
	lead_doc = frappe.get_doc("CRM Lead", lead)
	phone = lead_doc.get("mobile_no") or ""
	if not phone:
		frappe.throw("Lead chưa có số điện thoại")
	device_name = frappe.db.get_value(
		"Call Device", {"user": user, "active": 1}, "name", order_by="modified desc"
	)
	if not device_name:
		frappe.throw("Chưa gắn máy (Call Device). Đăng ký máy trước.")
	_expire_stale_jobs(device_name)
	job = frappe.get_doc(
		{
			"doctype": "Call Job",
			"lead": lead,
			"phone": phone,
			"device": device_name,
			"status": "Queued",
			"created_by_user": user,
			"expires_on": add_to_date(now_datetime(), minutes=JOB_TTL_MINUTES),
		}
	)
	job.insert()
	# FCM push would go here when fcm_token exists (Phase 4B optimization).
	return {"job": job.name, "lead": lead, "phone": phone, "device": device_name}


def _serialize_job(job_name):
	job = frappe.get_doc("Call Job", job_name)
	lead = frappe.get_doc("CRM Lead", job.lead)
	return {
		"job": job.name,
		"lead": job.lead,
		"lead_name": lead.get("lead_name") or "",
		"phone": job.phone,
		"status": job.status,
		"expires_on": str(job.expires_on),
	}


@frappe.whitelist(allow_guest=True)
def poll(device_token=None):
	"""PWA/Android long-poll (every 3s). Returns oldest Queued job, marks Delivered."""
	device = _get_device_by_token(device_token)
	if not device:
		frappe.throw("Unknown device_token", frappe.PermissionError)
	if not device.active:
		frappe.throw("Device is inactive", frappe.PermissionError)
	device.last_seen = now_datetime()
	device.save(ignore_permissions=True)
	_expire_stale_jobs(device.name)
	job_name = frappe.db.get_value(
		"Call Job",
		{"device": device.name, "status": "Queued"},
		"name",
		order_by="creation asc",
	)
	if not job_name:
		return {"job": None}
	frappe.db.set_value("Call Job", job_name, "status", "Delivered")
	return _serialize_job(job_name)


@frappe.whitelist(allow_guest=True)
def disposition(device_token=None, job=None, ket_qua=None, ly_do=None, ngay_hen=None):
	"""Sale submits call result. Creates Call Log -> hook updates lead care status."""
	device = _get_device_by_token(device_token)
	if not device:
		frappe.throw("Unknown device_token", frappe.PermissionError)
	if not job or not frappe.db.exists("Call Job", job):
		frappe.throw("Job not found")
	job_doc = frappe.get_doc("Call Job", job)
	if job_doc.device != device.name:
		frappe.throw("Job does not belong to this device", frappe.PermissionError)
	if job_doc.status in ("Closed", "Expired"):
		frappe.throw(f"Job already {job_doc.status}")
	if ket_qua not in RESULTS:
		frappe.throw(f"ket_qua must be one of: {', '.join(RESULTS)}")
	if ket_qua == "Hen goi lai" and not ngay_hen:
		frappe.throw("ngay_hen is required for Hen goi lai")

	log = frappe.get_doc(
		{
			"doctype": "Call Log",
			"lead": job_doc.lead,
			"phone": job_doc.phone,
			"nguon": "sim",
			"trang_thai_cuoc": "Dang goi",
			"sale": device.user,
			"device": device.name,
			"job": job_doc.name,
			"bat_dau": now_datetime(),
			"ket_thuc": now_datetime(),
		}
	)
	log.insert(ignore_permissions=True)
	# Fill result AFTER insert so the on_update hook sees a fresh ket_qua
	# (avoids Frappe defaulting Select to its first option at insert).
	log.ket_qua = ket_qua
	log.ly_do = ly_do or ""
	if ngay_hen:
		log.ngay_hen = ngay_hen
	log.save(ignore_permissions=True)

	job_doc.status = "Closed"
	job_doc.call_log = log.name
	job_doc.save(ignore_permissions=True)
	lead = frappe.get_doc("CRM Lead", job_doc.lead)
	return {
		"ok": True,
		"call_log": log.name,
		"care_status": lead.custom_care_status,
		"next_followup": str(lead.custom_next_followup or ""),
	}


@frappe.whitelist(allow_guest=True)
def skip_job(device_token=None, job=None):
	"""Sale presses Bo qua: close job as Expired without a Call Log."""
	device = _get_device_by_token(device_token)
	if not device:
		frappe.throw("Unknown device_token", frappe.PermissionError)
	if not job or not frappe.db.exists("Call Job", job):
		frappe.throw("Job not found")
	job_doc = frappe.get_doc("Call Job", job)
	if job_doc.device != device.name:
		frappe.throw("Job does not belong to this device", frappe.PermissionError)
	job_doc.status = "Expired"
	job_doc.save(ignore_permissions=True)
	return {"ok": True, "job": job_doc.name, "status": "Expired"}
