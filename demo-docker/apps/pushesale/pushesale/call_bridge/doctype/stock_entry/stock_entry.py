import frappe
from frappe.model.document import Document


class StockEntry(Document):
	def on_submit(self):
		from pushesale.stock import apply_entry

		apply_entry(self, 1)

	def on_cancel(self):
		from pushesale.stock import apply_entry

		apply_entry(self, -1)
