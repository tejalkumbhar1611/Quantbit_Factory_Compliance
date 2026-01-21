# Copyright (c) 2026, Quantbit Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname



class ComplianceMaster(Document):
	def before_insert(self):
		if not self.compliance_code:
			self.compliance_code = make_autoname(self.series + ".#####")

