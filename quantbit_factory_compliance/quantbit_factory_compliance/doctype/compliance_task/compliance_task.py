# Copyright (c) 2026, Quantbit Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ComplianceTask(Document):
	def before_submit(self):
		if not self.document:
			frappe.throw("Please upload document")
		else:
			self.status = "Completed"

