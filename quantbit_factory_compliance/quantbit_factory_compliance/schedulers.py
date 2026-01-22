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



# def create_new_frr():
#     try:
#         records = frappe.get_all(
#             "Compliance Task",
#             filters={"status": ["in", ["Completed", "Overdue"]]},
#             fields=["name", "reference_name", "due_date"]
#         )

#         today = getdate(nowdate())

#         for r in records:
#             # 🔹 Get latest FRR for this compliance
#             tasks = frappe.get_all(
#                 "Factory Regulatory Register",
#                 filters={"compliance": r.reference_name},
#                 fields=[
#                     "name",
#                     "factory",
#                     "unit",
#                     "assigned_owner",
#                     "category",
#                     "compliance",
#                     "compliance_name",
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

#             # 🔹 Overdue check
#             grace_days = task.grace_days or 0
#             overdue_date = add_days(getdate(r.due_date), grace_days)

#             # if overdue_date < today:
#             #     compliance_status = "Closed"
#             #     frr_status = "Completed"
#             # else:
#             #     compliance_status = "Closed"
#             #     frr_status = "Completed"

#             # 🔹 Update old records
#             frappe.db.set_value(
#                 "Compliance Task",
#                 r.name,
#                 "status",
#                 "Closed"
#             )

#             frappe.db.set_value(
#                 "Factory Regulatory Register",
#                 task.name,
#                 "compliance_status",
#                 "Completed"
#             )

#             # 🔹 CREATE NEW FRR (if frequency based)
#             if task.frequency and task.period_to:
#                 period_from = add_days(getdate(task.period_to), 1)

#                 if task.frequency == "Monthly":
#                     period_to = add_months(period_from, 1)
#                 elif task.frequency == "Quarterly":
#                     period_to = add_months(period_from, 3)
#                 elif task.frequency == "Half-Yearly":
#                     period_to = add_months(period_from, 6)
#                 elif task.frequency == "Yearly":
#                     period_to = add_months(period_from, 12)
#                 else:
#                     continue
                
#                 due_date = get_due_date(period_from, task.due_day)

#                 new_frr = frappe.new_doc("Factory Regulatory Register")
#                 new_frr.factory = task.factory
#                 new_frr.unit = task.unit
#                 new_frr.assigned_owner = task.assigned_owner
#                 new_frr.category = task.category
#                 new_frr.compliance = task.compliance
#                 new_frr.compliance_name = task.compliance_name
#                 new_frr.frequency = task.frequency
#                 new_frr.referance_no = task.referance_no
#                 new_frr.period_from = period_from
#                 new_frr.period_to = period_to
#                 new_frr.due_day = task.due_day
#                 new_frr.status = "Pending"
#                 new_frr.due_date = due_date

#                 new_frr.insert(ignore_permissions=True)
#                 new_frr.submit()

#         frappe.db.commit()


#     except Exception:
#         frappe.log_error(
#             message=frappe.get_traceback(),
#             title="create_new_frr scheduler failed"
#         )



# def create_license_task():
#     records = frappe.get_all(
#         "Factory Regulatory Register",
#         filters={"category":"License","status": "Expired"},
#         fields=["name","license","assigned_owner","valid_upto","license_no"]
#     )

#     for r in records:
#         if frappe.db.exists(
#             "License Task",
#             {
#                 "license_name": r.license,
#                 "license_no":r.license_no,
#                 "valid_upto":r.valid_upto
#             }
#         ):
#             continue
#         task = frappe.new_doc("License Task")
#         task.license_name = r.name
#         task.license_no = r.license_no
#         task.assigned_to = r.assigned_owner
#         task.status = "Under Renewal"
#         task.valid_upto = r.valid_upto
#         task.task_name = r.license

#         task.insert(ignore_permissions=True)
#         task.save()


# def create_license_frr():
#     try:
#         records = frappe.get_all(
#             "License Task",
#             filters={"status": "Renewed"},
#             fields=[
#                 "name",
#                 "license_name",
#                 "license_no"
#             ]
#         )

#         for r in records:
#             tasks = frappe.get_all(
#                 "Factory Regulatory Register",
#                 filters={
#                     "license" : r.license_name,
#                     "license_no": r.license_no
#                 },
#                 fields=[
#                     "name",
#                     "factory",
#                     "unit",
#                     "assigned_owner",
#                     "license",
#                     "license_no",
#                     "valid_upto",
#                     "status"
#                 ],
#                 order_by="valid_upto desc",
#                 limit=1
#             )

#             if not tasks:
#                 continue

#             task = tasks[0]

#             frappe.db.set_value(
#                 "License Task",
#                 r.name,
#                 "status",
#                 "Closed"
#             )

#             frappe.db.set_value(
#                 "Factory Regulatory Register",
#                 task.name,
#                 "status",
#                 "Completed"
#             )

#             validity_months = frappe.db.get_value(
#                 "License",
#                 r.license_name,
#                 "validity_period_months"
#             )

#             if not validity_months:
#                 continue

#             valid_from = getdate(task.valid_upto)
#             valid_upto = add_months(valid_from, int(validity_months))

#             new_frr = frappe.new_doc("Factory Regulatory Register")

#             new_frr.factory = task.factory
#             new_frr.unit = task.unit
#             new_frr.assigned_owner = task.assigned_owner
#             new_frr.category = "License"
#             new_frr.license = r.task_name
#             new_frr.license_no = r.license_no
#             new_frr.frequency = "One-time"
#             new_frr.issued_on = valid_from
#             new_frr.valid_upto = valid_upto
#             new_frr.status = "Active"

#             new_frr.insert(ignore_permissions=True)

#         frappe.db.commit()

#     except Exception:
#         frappe.log_error(
#             message=frappe.get_traceback(),
#             title="create_license_frr scheduler failed"
#         )





# def get_due_date(period_from, due_day):
#     if not due_day:
#         return None

#     period_from = getdate(period_from)
#     last_day = calendar.monthrange(period_from.year, period_from.month)[1]

#     day = min(int(due_day), last_day)
#     return period_from.replace(day=day)





# def submit_all_frr():
#     task_submit = frappe.get_all("Factory Regulatory Register", filters={"docstatus":1}, fields=["name"])
#     for task in task_submit:
#         frappe.db.set_value("Factory Regulatory Register",task.name,"docstatus",2)







# def create_license_task():
#     records = frappe.get_all(
#         "Factory Regulatory Register",
#         filters={"category":"License","status": "Expired"},
#         fields=[
#             "name",
#             "license",
#             "license_no",
#             "assigned_owner",
#             "valid_upto"
#         ]
#     )

#     for r in records:
#         license_doc = frappe.get_value(
#             "License",
#             {"name": r.license},
#             "name"
#         )

#         if not license_doc:
#             frappe.log_error(
#                 f"License not found: {r.license}",
#                 "License Task Creation Failed"
#             )
#             continue

#         if frappe.db.exists(
#             "License Task",
#             {
#                 "name": license_doc,
#                 "valid_upto": r.valid_upto
#             }
#         ):
#             continue

#         task = frappe.new_doc("License Task")
#         task.license_name = license_doc
#         task.license_no = r.license_no
#         task.assigned_to = r.assigned_owner
#         task.status = "Under Renewal"
#         task.posting_date = today()
#         task.valid_upto = r.valid_upto
#         task.task_name = f"Upload Document for Compliance {r.license}"

#         task.insert(ignore_permissions=True)

#         frappe.db.set_value(
#             "Factory Regulatory Register",
#             r.name,
#             "status",
#             "Under Renewal"
#         )

#     frappe.db.commit()



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

