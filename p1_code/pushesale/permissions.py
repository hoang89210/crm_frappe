"""Row-level permissions for pushesale doctypes.

CRM Lead keeps CRM's native org_hierarchy rules (lead_owner based) — do NOT
override here. Sales User sees own lead_owner records; Sales Manager sees all
when hierarchy is disabled. See README assumptions.
"""

import frappe


def _is_privileged(user):
	if user == "Administrator":
		return True
	roles = set(frappe.get_roles(user))
	return bool(roles & {"System Manager", "Sales Manager"})


def call_device_query(user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	return f"`tabCall Device`.`user` = {frappe.db.escape(user)}"


def has_call_device_permission(doc, ptype="read", user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return True
	if ptype == "create" or not getattr(doc, "name", None):
		return True
	return doc.get("user") == user


def call_job_query(user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	u = frappe.db.escape(user)
	return (
		"`tabCall Job`.`created_by_user` = {u} OR `tabCall Job`.`device` IN "
		"(SELECT `name` FROM `tabCall Device` WHERE `user` = {u})"
	).format(u=u)


def has_call_job_permission(doc, ptype="read", user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return True
	if ptype == "create" or not getattr(doc, "name", None):
		return True
	if doc.get("created_by_user") == user:
		return True
	device_user = frappe.db.get_value("Call Device", doc.get("device"), "user")
	return device_user == user


def call_log_query(user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	return f"`tabCall Log`.`sale` = {frappe.db.escape(user)}"


def has_call_log_permission(doc, ptype="read", user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return True
	if ptype == "create" or not getattr(doc, "name", None):
		return True
	return doc.get("sale") == user
