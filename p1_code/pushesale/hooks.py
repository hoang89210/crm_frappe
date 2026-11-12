from . import __version__ as app_version

app_name = "pushesale"
app_title = "Pushesale"
app_publisher = "Your Company"
app_description = "Frappe app to replace basic Pushsale features with CRM + Chatwoot + SIM call"
app_email = "you@example.com"
app_license = "MIT"

after_install = "pushesale.install.after_install"

fixtures = [
	"Custom Field",
]

permission_query_conditions = {
	"Call Device": "pushesale.permissions.call_device_query",
	"Call Job": "pushesale.permissions.call_job_query",
	"Call Log": "pushesale.permissions.call_log_query",
}

has_permission = {
	"Call Device": "pushesale.permissions.has_call_device_permission",
	"Call Job": "pushesale.permissions.has_call_job_permission",
	"Call Log": "pushesale.permissions.has_call_log_permission",
}
