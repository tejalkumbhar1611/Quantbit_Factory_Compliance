# import frappe
# from frappe.utils import getdate, today, add_days


# def send_compliance_due_notifications():
#     today_date = getdate(today())

#     records = frappe.get_all(
#         "Factory Regulatory Register",
#         filters={
#             "category": "Compliance",
#             "compliance_status": ["in", ["Pending", "Submitted"]],
#             "due_date": ["!=", None],
#             "assigned_owner": ["!=", None],
#         },
#         fields=[
#             "name",
#             "due_date",
#             "assigned_owner",
#             "compliance_name"
#         ]
#     )
#     if records:
#         frappe.log_error("Found compliance records for notification.")
#     else:
#         frappe.log_error("No compliance records found for notification.")

#     for r in records:
#         due_date = getdate(r.due_date)

#         for days in (30, 15, 7):
#             notify_date = add_days(due_date, -days)

#             if today_date == notify_date:
#                 send_notification(r, days)


# def send_notification(doc, days):
#     frappe.sendmail(
#         recipients=[doc.assigned_owner],
#         subject=f"Compliance Due in {days} Days",
#         message=f"""
#         <p>Hello,</p>

#         <p><b>{doc.compliance_name or doc.name}</b> is due in
#         <b>{days} days</b>.</p>

#         <p>Please upload required documents before the due date.</p>

#         <p>Regards,<br>
#         Factory Compliance System</p>
#         """
#     )
