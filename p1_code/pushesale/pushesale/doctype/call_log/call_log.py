import frappe
from frappe.model.document import Document


class CallLog(Document):
	def on_update(self):
		# Update lead care status only when ket_qua was just filled.
		from pushesale.api.care import apply_call_result

		apply_call_result(self)
