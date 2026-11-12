dst = "/home/frappe/frappe-bench/apps/pushesale/pushesale/api/chatwoot.py"
src = open(dst, encoding="utf-8").read()
if "def open_conversation" in src:
    print("api already has open_conversation")
else:
    fn = '''
@frappe.whitelist()
def open_conversation(lead):
	"""URL for the sale to open this lead's Chatwoot thread (or the inbox)."""
	if not lead or not frappe.db.exists("CRM Lead", lead):
		frappe.throw("Không thấy lead")
	if not frappe.has_permission("CRM Lead", "read", lead):
		frappe.throw("Không có quyền", frappe.PermissionError)
	base = (_conf("CHATWOOT_URL") or "").rstrip("/")
	account_id = (_conf("CHATWOOT_ACCOUNT_ID") or "").strip()
	if not base or not account_id:
		frappe.throw("Chưa kết nối Chatwoot. Vào Kênh để điền URL và Account ID.")
	conv = frappe.db.get_value("CRM Lead", lead, "custom_chatwoot_conversation_id")
	if conv:
		url = f"{base}/app/accounts/{account_id}/conversations/{conv}"
	else:
		url = f"{base}/app/accounts/{account_id}"
	return {"url": url, "has_conversation": bool(conv)}


'''
    needle = "def _chatwoot_creds("
    if needle not in src:
        raise SystemExit("anchor missing")
    src = src.replace(needle, fn + needle, 1)
    open(dst, "w", encoding="utf-8").write(src)
    print("api patched")
