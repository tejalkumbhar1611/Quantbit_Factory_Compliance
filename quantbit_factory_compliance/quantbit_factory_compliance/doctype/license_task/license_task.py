# Copyright (c) 2026, Quantbit Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
    nowdate,
    getdate,
    add_months,
    add_days
)


class LicenseTask(Document):
	def before_submit(self):
		if not self.document:
			frappe.throw("Please upload document")


	def on_submit(self):
		frappe.db.set_value(
                "License Task",
                self.name,
                "status",
                "Closed"
            )

		doc = frappe.get_doc("Factory Regulatory Register",{"name":self.license_name})

		frappe.db.set_value(
			"Factory Regulatory Register",
			doc.name,
			"status",
			"Completed"
		)

		frappe.db.set_value(
			"Factory Regulatory Register",
			doc.name,
			"document",
			self.document
		)

		validity_months = frappe.db.get_value(
                "License",
                doc.license,
                "validity_period_months"
            )
		
		valid_from = getdate(doc.valid_upto)
		valid_upto = add_months(valid_from, int(validity_months))
		

		new_frr = frappe.new_doc("Factory Regulatory Register")

		new_frr.factory = doc.factory
		new_frr.unit = doc.unit
		new_frr.category = doc.category
		new_frr.assigned_owner = doc.assigned_owner
		new_frr.license = doc.license
		new_frr.license_no = doc.license_no
		new_frr.status = "Active"
		new_frr.issued_on = self.posting_date
		new_frr.alert_before_days = doc.alert_before_days
		new_frr.valid_upto = valid_upto

		new_frr.insert(ignore_permissions=True)

		frappe.db.commit()