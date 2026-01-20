# Copyright (c) 2026, Quantbit Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days
from datetime import date
import calendar


class FactoryRegulatoryRegister(Document):

    def validate(self):
        self.calculate_due_date()
        self.set_compliance_status()


    def calculate_due_date(self):
        if self.category != "Compliance":
            return

        if not self.period_to or not self.frequency or not self.due_day:
            return

        period_to = getdate(self.period_to)
        due_day = int(self.due_day)
        year = period_to.year
        month = period_to.month

        if self.frequency == "One-time":
            self.due_date = period_to
            return

        
        if self.frequency == "Monthly":
            month_increment = 1
        elif self.frequency == "Quarterly":
            month_increment = 3
        elif self.frequency == "Half-Yearly":
            month_increment = 6
        elif self.frequency == "Yearly":
            month_increment = 12
        else:
            month_increment = 1  

        
        month += month_increment
        while month > 12:
            month -= 12
            year += 1

        
        last_day_of_month = calendar.monthrange(year, month)[1]
        if due_day > last_day_of_month:
            due_day = last_day_of_month

        self.due_date = date(year, month, due_day)

   
    def set_compliance_status(self):
        if self.category != "Compliance":
            return

       
        self.compliance_status = "Pending"

        
        if self.docstatus == 1:
            self.compliance_status = "Submitted"

    
        if self.due_date:
            due_date = getdate(self.due_date)
            grace_days = int(self.grace_days or 0)
            overdue_date = add_days(due_date, grace_days)

            if getdate(today()) > overdue_date:
                self.compliance_status = "Overdue"
                return

    
        if self.document and self.due_date:
            if getdate(today()) <= overdue_date:
                self.compliance_status = "Approved"

@frappe.whitelist()
def send_compliance():
    frappe.log_error(f"Scheduler running at {today()}", "Compliance Scheduler Started")
    today_date = getdate(today())
    
   
    compliance_records = frappe.get_all(
        "Factory Regulatory Register",
        filters={
            "category": "Compliance",
            "compliance_status": "Pending",
            "due_date": ["!=", None],
            "assigned_owner": ["!=", None],
        },
        fields=[
            "name",
            "due_date",
            "assigned_owner",
            "compliance_name",
            "category",
            "document",
            "license"
        ]
    )
    
    license_records = frappe.get_all(
        "Factory Regulatory Register",
        filters={
            "category": "License",
            "valid_upto": ["!=", None],
            "assigned_owner": ["!=", None],
        },
        fields=[
            "name",
            "valid_upto",
            "assigned_owner",
            "license_no",
            "category",
            "document",
            "license",
            "alert_before_days"
        ]
    )
    
    if compliance_records:
        frappe.log_error("Found compliance records for notification.")
    else:
        frappe.log_error("No compliance records found for notification.")
    
    if license_records:
        frappe.log_error("Found license records for notification.")
    else:
        frappe.log_error("No license records found for notification.")

    
    for r in compliance_records:
        due_date = getdate(r.due_date)

        for days in (30, 15, 7):
            notify_date = add_days(due_date, -days)
            frappe.log_error(f"Checking: {r.name} | Due: {due_date} | Notify: {notify_date} | Today: {today_date} | Days: {days}", "Notification Check")

            if today_date == notify_date:
                send_notification(r, days)
    
  
    for r in license_records:
        valid_upto = getdate(r.valid_upto)
        alert_days = int(r.alert_before_days or 30)
        notify_date = add_days(valid_upto, -alert_days)
        
        frappe.log_error(f"Checking License: {r.name} | Valid Upto: {valid_upto} | Notify: {notify_date} | Today: {today_date} | Days: {alert_days}", "License Notification Check")

        if today_date == notify_date:
            send_notification(r, alert_days)


def send_notification(doc, days):
    if doc.category == "Compliance":
        due_date = getdate(doc.due_date) if doc.due_date else None
        category_item = doc.compliance_name or "Not specified"
        subject_text = "Compliance Due"
        message_text = f"<p><b>{category_item}</b> (Compliance) is due on <b>{due_date}</b> (in <b>{days} days</b>).</p><p>Please upload required documents before the due date.</p>"
    else:  
        due_date = getdate(doc.valid_upto) if doc.valid_upto else None
        category_item = doc.license_no or "Not specified"
        subject_text = "License Expiry Alert"
        message_text = f"<p><b>{category_item}</b> (License) will expire on <b>{due_date}</b> (in <b>{days} days</b>).</p><p>Please renew the license before the expiry date.</p>"
    
    frappe.log_error(
        f"Sending notification to {doc.assigned_owner} for {doc.name} - {subject_text} in {days} days", "Notification Sent"
    )
    frappe.sendmail(
        recipients=[doc.assigned_owner],
        subject=f"{subject_text} in {days} Days",
        message=f"""
        <p>Hello,</p>

        {message_text}

        <p>Document: <b>{doc.name}</b></p>

        <p>Regards,<br>
        Factory Compliance System</p>
        """
    )

            