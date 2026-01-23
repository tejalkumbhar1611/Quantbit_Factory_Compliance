import frappe
from frappe.utils import today
import calendar
from frappe.utils import (
    nowdate,
    getdate,
    add_months,
    add_days
)

"""Compliance task Schedulers"""


def create_compliance_task():
    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={"category":"Compliance","compliance_status": "Pending","due_date": ["<=", today()]},
        fields=["name","compliance","assigned_owner","due_date","referance_no","period_from","period_to"]
    )

    for r in records:
        if frappe.db.exists(
            "Compliance Task",
            {
                "reference_doctype": r.name,
                "due_date":r.due_date
            }
        ):
            continue
        task = frappe.new_doc("Compliance Task")
        task.reference_doctype = r.name
        task.reference_name = r.compliance
        task.assigned_to = r.assigned_owner
        task.status = "Pending"
        task.period_from = r.period_from
        task.period_to = r.period_to
        task.posting_date = today()
        task.due_date = r.due_date
        task.task_name = f"Upload Document for Compliance {r.referance_no}"

        task.insert(ignore_permissions=True)
        task.save()



"""License task Schedulers"""


def create_license_task():
    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={
            "category": "License",
            "status": "Active",
            "due_date": ["<=", today()]
        },
        fields=[
            "name",
            "license",
            "assigned_owner",
            "valid_upto",
            "license_no",
            "due_date",
            "issued_on"
        ]
    )

    for r in records:
        if frappe.db.exists(
            "License Task",
            {
                "license_name": r.license,
                "due_date": r.due_date
            }
        ):
            continue

        task = frappe.new_doc("License Task")
        task.referance_doctype = r.name
        task.license_name = r.license
        task.license_no = r.license_no
        task.assigned_to = r.assigned_owner
        task.status = "Under Renewal"
        task.valid_upto = r.valid_upto
        task.task_name = f"Task for {r.license} license renewal"
        task.due_date = r.due_date
        task.issued_on = r.issued_on
        task.posting_date = today()

        task.insert(ignore_permissions=True)

    frappe.db.commit()



"""License Expiry Schedulers"""


def expire_license_frr():
    today_date = getdate(today())

    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={
            "category": "License",
            "status": ["!=", "Expired"],
            "valid_upto": ["<", today_date],
        },
        fields=["name"]
    )

    for r in records:
        frappe.db.set_value(
            "Factory Regulatory Register",
            r.name,
            "status",
            "Expired"
        )

    frappe.db.commit()



""" Update Overdue Status """


def overdue_status_compliance_task():
    tasks = frappe.get_all(
        "Compliance Task",
        filters={"status": "Pending","period_to": ["<", today()]},
        fields=["name"]
    )
    
    for task in tasks:
        task.status = "Overdue"
        task.save(ignore_permissions=True)


""" Update Closing Status for tasks """


def close_compliance_task_status():
    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={
            "category": "Compliance",
            "compliance_status": "Closed"
        },
        fields=["name", "compliance"]
    )

    for r in records:
        tasks = frappe.get_all(
            "Compliance Task",
            filters={
                "reference_name": r.compliance
            },
            fields=["name"]
        )

        for t in tasks:
            frappe.db.set_value(
                "Compliance Task",
                t.name,
                "status",
                "Closed"
            )

    frappe.db.commit()


def close_license_task_status():
    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={
            "category": "License",
            "status": "Closed"
        },
        fields=["name", "compliance"]
    )

    for r in records:
        tasks = frappe.get_all(
            "License Task",
            filters={
                "referance_doctype": r.name,
                "reference_name": r.compliance
            },
            fields=["name"]
        )

        for t in tasks:
            frappe.db.set_value(
                "License Task",
                t.name,
                "status",
                "Closed"
            )

    frappe.db.commit()




""" Notification Schedulers """


def send_factory_regulatory_notifications():
    today = nowdate()

    records = frappe.get_all(
        "Factory Regulatory Register",
        fields=[
            "name",
            "category",
            "due_date",
            "alert_before_days",
            "assigned_owner"
        ],
        filters={
            "docstatus": 1,
            "due_date": ["<=", today]
        }
    )

    for rec in records:
        if not rec.assigned_owner:
            continue

        message = (
            f"{rec.category} '{rec.name}' is due for action. "
            f"Notification was scheduled {rec.alert_before_days} day(s) in advance."
        )

        send_system_notification(
            user=rec.assigned_owner,
            subject=f"{rec.category} Alert",
            message=message
        )

        send_bell_notification(
            user=rec.assigned_owner,
            subject=f"{rec.category} Alert",
            message=message
        )

        user_email = frappe.db.get_value("User", rec.assigned_owner, "email")

        if user_email:
            send_email_notification(
                recipients=[user_email],
                subject=f"{rec.category} Alert",
                message=message
            )


def send_system_notification(user, subject, message):
    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": subject,
        "email_content": message,
        "for_user": user,
        "type": "Alert"
    }).insert(ignore_permissions=True)


def send_email_notification(recipients, subject, message):
    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message
    )


def send_bell_notification(user, subject, message):
    frappe.publish_realtime(
        event="notification",
        message={
            "type": "Alert",
            "subject": subject,
            "message": message
        },
        user=user
    )
