"""Pushesale Settings (Single): Chatwoot + Facebook tokens."""

import frappe

SETTINGS_DOCTYPE = "Pushesale Settings"
SETTINGS_ROLES = {"System Manager", "Sales Manager", "Marketing"}
PASSWORD_FIELDS = (
	"chatwoot_api_token",
	"chatwoot_webhook_secret",
	"facebook_access_token",
	"meta_app_secret",
)
CONF_MAP = {
	"CHATWOOT_URL": ("chatwoot_url", False),
	"CHATWOOT_ACCOUNT_ID": ("chatwoot_account_id", False),
	"CHATWOOT_API_TOKEN": ("chatwoot_api_token", True),
	"CHATWOOT_WEBHOOK_SECRET": ("chatwoot_webhook_secret", True),
	"META_APP_SECRET": ("meta_app_secret", True),
	"META_VERIFY_TOKEN": ("meta_verify_token", False),
}


def require_settings_role():
	user = frappe.session.user
	if user in (None, "Guest"):
		frappe.throw("Cần đăng nhập.", frappe.PermissionError)
	if user == "Administrator":
		return
	if not (set(frappe.get_roles(user)) & SETTINGS_ROLES):
		frappe.throw("Không có quyền cấu hình kênh.", frappe.PermissionError)


def mask_secret(value):
	if not value:
		return ""
	text = str(value)
	if len(text) <= 4:
		return "****"
	return "****" + text[-4:]


def should_keep_secret(value):
	if value is None:
		return True
	text = str(value).strip()
	return (not text) or text.startswith("****")


def conf_value(key):
	"""Settings first, then site_config. Password fields decrypted."""
	conf_val = ""
	try:
		raw = frappe.conf.get(key) if hasattr(frappe, "conf") else ""
		conf_val = str(raw).strip() if raw else ""
	except Exception:
		conf_val = ""

	spec = CONF_MAP.get(key)
	settings_val = ""
	if spec:
		field, is_password = spec
		try:
			if is_password:
				from frappe.utils.password import get_decrypted_password

				settings_val = (
					get_decrypted_password(
						SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, field, raise_exception=False
					)
					or ""
				)
			else:
				settings_val = frappe.db.get_single_value(SETTINGS_DOCTYPE, field) or ""
		except Exception:
			settings_val = ""
		settings_val = str(settings_val).strip() if settings_val else ""
	return settings_val or conf_val


def get_password_field(field):
	try:
		from frappe.utils.password import get_decrypted_password

		return (
			get_decrypted_password(
				SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, field, raise_exception=False
			)
			or ""
		)
	except Exception:
		return ""


def get_settings_doc():
	return frappe.get_single(SETTINGS_DOCTYPE)


def _plain(field):
	try:
		return frappe.db.get_single_value(SETTINGS_DOCTYPE, field) or ""
	except Exception:
		return ""


def _as_check(val, default=0):
	if val is None or val == "":
		return default
	if val in (True, 1, "1", "true", "True", "on"):
		return 1
	return 0


def public_webhook_urls():
	base = (frappe.utils.get_url() or "").rstrip("/")
	cw_secret = conf_value("CHATWOOT_WEBHOOK_SECRET") or "change-me"
	meta_verify = conf_value("META_VERIFY_TOKEN")
	return {
		"chatwoot_webhook_url": (
			f"{base}/api/method/pushesale.api.chatwoot.webhook?secret={cw_secret}"
			if base
			else ""
		),
		"meta_webhook_url": (
			f"{base}/api/method/pushesale.api.meta.webhook" if base else ""
		),
		"meta_verify_token": meta_verify or "",
	}


@frappe.whitelist()
def get_settings():
	require_settings_role()
	urls = public_webhook_urls()
	return {
		"chatwoot_url": _plain("chatwoot_url"),
		"chatwoot_account_id": _plain("chatwoot_account_id"),
		"chatwoot_api_token": mask_secret(get_password_field("chatwoot_api_token")),
		"chatwoot_webhook_secret": mask_secret(get_password_field("chatwoot_webhook_secret")),
		"chatwoot_sync_enabled": int(_plain("chatwoot_sync_enabled") or 0),
		"chatwoot_last_sync": str(_plain("chatwoot_last_sync") or ""),
		"chatwoot_last_result": _plain("chatwoot_last_result"),
		"facebook_page_url": _plain("facebook_page_url"),
		"facebook_access_token": mask_secret(get_password_field("facebook_access_token")),
		"facebook_page_id": _plain("facebook_page_id"),
		"facebook_page_name": _plain("facebook_page_name"),
		"facebook_sync_enabled": int(_plain("facebook_sync_enabled") or 0),
		"facebook_last_sync": str(_plain("facebook_last_sync") or ""),
		"facebook_last_result": _plain("facebook_last_result"),
		"chatwoot_webhook_url": urls["chatwoot_webhook_url"],
		"meta_webhook_url": urls["meta_webhook_url"],
	}


@frappe.whitelist()
def save_settings(
	chatwoot_url=None,
	chatwoot_account_id=None,
	chatwoot_api_token=None,
	chatwoot_webhook_secret=None,
	chatwoot_sync_enabled=None,
	facebook_page_url=None,
	facebook_access_token=None,
	facebook_sync_enabled=None,
):
	require_settings_role()
	doc = get_settings_doc()
	if chatwoot_url is not None:
		doc.chatwoot_url = str(chatwoot_url).strip()
	if chatwoot_account_id is not None:
		doc.chatwoot_account_id = str(chatwoot_account_id).strip()
	if not should_keep_secret(chatwoot_api_token):
		doc.chatwoot_api_token = str(chatwoot_api_token).strip()
	if not should_keep_secret(chatwoot_webhook_secret):
		doc.chatwoot_webhook_secret = str(chatwoot_webhook_secret).strip()
	if chatwoot_sync_enabled is not None:
		doc.chatwoot_sync_enabled = _as_check(chatwoot_sync_enabled, 0)
	if facebook_page_url is not None:
		doc.facebook_page_url = str(facebook_page_url).strip()
	if not should_keep_secret(facebook_access_token):
		doc.facebook_access_token = str(facebook_access_token).strip()
	if facebook_sync_enabled is not None:
		doc.facebook_sync_enabled = _as_check(facebook_sync_enabled, 1)
	doc.save(ignore_permissions=True)
	return get_settings()
