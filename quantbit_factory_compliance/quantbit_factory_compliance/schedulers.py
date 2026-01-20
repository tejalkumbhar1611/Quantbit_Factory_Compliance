import frappe
from frappe.utils import today
import calendar
from frappe.utils import (
    nowdate,
    getdate,
    add_months,
    add_days
)

"""Compliance Schedulers"""


def print_msg():
    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={"category":"Compliance","compliance_status": "Pending","period_to": ["<=", today()]},
        fields=["name","compliance","assigned_owner","due_date","referance_no"]
    )

    for r in records:
        if frappe.db.exists(
            "Compliance Task",
            {
                "reference_name": r.compliance,
                "due_date":r.due_date
            }
        ):
            continue
        task = frappe.new_doc("Compliance Task")
        task.reference_doctype = r.name
        task.reference_name = r.compliance
        task.assigned_to = r.assigned_owner
        task.status = "Pending"
        task.posting_date = today()
        task.due_date = r.due_date
        task.task_name = f"Upload Document for Compliance {r.referance_no}"

        task.insert(ignore_permissions=True)
        task.save()



def create_new_frr():
    try:
        records = frappe.get_all(
            "Compliance Task",
            filters={"status": ["in", ["Completed", "Overdue"]]},
            fields=["name", "reference_name", "due_date"]
        )

        today = getdate(nowdate())

        for r in records:
            # 🔹 Get latest FRR for this compliance
            tasks = frappe.get_all(
                "Factory Regulatory Register",
                filters={"compliance": r.reference_name},
                fields=[
                    "name",
                    "factory",
                    "unit",
                    "assigned_owner",
                    "category",
                    "compliance",
                    "compliance_name",
                    "frequency",
                    "referance_no",
                    "period_to",
                    "grace_days",
                    "due_day"
                ],
                order_by="period_to desc",
                limit=1
            )

            if not tasks:
                continue

            task = tasks[0]

            # 🔹 Overdue check
            grace_days = task.grace_days or 0
            overdue_date = add_days(getdate(r.due_date), grace_days)

            # if overdue_date < today:
            #     compliance_status = "Closed"
            #     frr_status = "Completed"
            # else:
            #     compliance_status = "Closed"
            #     frr_status = "Completed"

            # 🔹 Update old records
            frappe.db.set_value(
                "Compliance Task",
                r.name,
                "status",
                "Closed"
            )

            frappe.db.set_value(
                "Factory Regulatory Register",
                task.name,
                "compliance_status",
                "Completed"
            )

            # 🔹 CREATE NEW FRR (if frequency based)
            if task.frequency and task.period_to:
                period_from = add_days(getdate(task.period_to), 1)

                if task.frequency == "Monthly":
                    period_to = add_months(period_from, 1)
                elif task.frequency == "Quarterly":
                    period_to = add_months(period_from, 3)
                elif task.frequency == "Half-Yearly":
                    period_to = add_months(period_from, 6)
                elif task.frequency == "Yearly":
                    period_to = add_months(period_from, 12)
                else:
                    continue
                
                due_date = get_due_date(period_from, task.due_day)

                new_frr = frappe.new_doc("Factory Regulatory Register")
                new_frr.factory = task.factory
                new_frr.unit = task.unit
                new_frr.assigned_owner = task.assigned_owner
                new_frr.category = task.category
                new_frr.compliance = task.compliance
                new_frr.compliance_name = task.compliance_name
                new_frr.frequency = task.frequency
                new_frr.referance_no = task.referance_no
                new_frr.period_from = period_from
                new_frr.period_to = period_to
                new_frr.due_day = task.due_day
                new_frr.status = "Pending"
                new_frr.due_date = due_date

                new_frr.insert(ignore_permissions=True)
                new_frr.submit()

        frappe.db.commit()

    except Exception:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="create_new_frr scheduler failed"
        )

def get_due_date(period_from, due_day):
    if not due_day:
        return None

    period_from = getdate(period_from)
    last_day = calendar.monthrange(period_from.year, period_from.month)[1]

    day = min(int(due_day), last_day)
    return period_from.replace(day=day)


def submit_all_frr():
    task_submit = frappe.get_all("Factory Regulatory Register", filters={"docstatus":0}, fields=["name"])
    for task in task_submit:
        frappe.db.set_value("Factory Regulatory Register",task.name,"docstatus",1)

# def create_new_frr():
#     try:
#         records = frappe.get_all(
#             "Compliance Task",
#             filters={"status": ["in",["Completed","Overdue"]]},
#             fields=["name", "reference_name", "due_date"]
#         )

#         today = getdate(nowdate())

#         for r in records:
#             tasks = frappe.get_all(
#                 "Factory Regulatory Register",
#                 filters={"name": r.reference_doctype},
#                 fields=[
#                     "name",
#                     "factory",
#                     "unit",
#                     "assigned_owner",
#                     "category",
#                     "compliance",
#                     "compliance_name"
#                     "frequency",
#                     "referance_no",
#                     "period_to",
#                     "grace_days",
#                     "due_day"
#                 ],
#                 order_by="period_to desc",
#                 limit=1
#             )

#             if not tasks:
#                 continue

#             task = tasks[0]

#             grace_days = task.grace_days
#             overdue_date = add_days(getdate(r.due_date), grace_days)

#             if overdue_date < today:
#                 compliance_status = "Completed"
#                 frr_status = "Overdue"
#             else:
#                 frr_status = "Closed"

#             frappe.db.set_value(
#                 "Compliance Task",
#                 r.name,
#                 "status",
#                 compliance_status
#             )

#             frappe.db.set_value(
#                 "Factory Regulatory Register",
#                 task.name,
#                 "compliance_status",
#                 frr_status
#             )

#             frappe.db.commit()

    # except Exception:
    #     frappe.log_error(
    #         title="Compliance Overdue Status Update Failed",
    #         message=frappe.get_traceback()
    #     )



""" License Schedulers """



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




def create_license_task():
    records = frappe.get_all(
        "Factory Regulatory Register",
        filters={"category":"License","status": "Expired"},
        fields=[
            "name",
            "license",
            "license_no",
            "assigned_owner",
            "valid_upto"
        ]
    )

    for r in records:
        license_doc = frappe.get_value(
            "License",
            {"name": r.license},
            "name"
        )

        if not license_doc:
            frappe.log_error(
                f"License not found: {r.license}",
                "License Task Creation Failed"
            )
            continue

        if frappe.db.exists(
            "License Task",
            {
                "name": license_doc,
                "valid_upto": r.valid_upto
            }
        ):
            continue

        task = frappe.new_doc("License Task")
        task.license_name = license_doc
        task.license_no = r.license_no
        task.assigned_to = r.assigned_owner
        task.status = "Under Renewal"
        task.posting_date = today()
        task.valid_upto = r.valid_upto
        task.task_name = f"Upload Document for Compliance {r.license}"

        task.insert(ignore_permissions=True)

        frappe.db.set_value(
            "Factory Regulatory Register",
            r.name,
            "status",
            "Renewal Initiated"
        )

    frappe.db.commit()



# def print_msg():
#     records = frappe.get_all(
#         "Factory Regulatory Register",
#         filters={"compliance_status": "Pending","period_to": ["<=", today()]},
#         fields=["name","compliance","assigned_owner","due_date","referance_no"]
#     )

#     for r in records:
#         if frappe.db.exists(
#             "Compliance Task",
#             {
#                 "reference_name": r.compliance,
#                 "due_date":r.due_date
#             }
#         ):
#             continue
#         task = frappe.new_doc("Compliance Task")
#         task.reference_doctype = r.name
#         task.reference_name = r.compliance
#         task.assigned_to = r.assigned_owner
#         task.status = "Pending"
#         task.posting_date = today()
#         task.due_date = r.due_date
#         task.task_name = f"Upload Document for Compliance {r.referance_no}"

#         task.insert(ignore_permissions=True)
#         task.save()

