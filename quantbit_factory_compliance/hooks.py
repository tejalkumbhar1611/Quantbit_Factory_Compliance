app_name = "quantbit_factory_compliance"
app_title = "Quantbit Factory Compliance"
app_publisher = "Quantbit Technologies"
app_description = "Factory Compliance System"
app_email = "contact@erpdata.in"
app_license = "mit"


fixtures = [
    {
        "dt": "Number Card",
        "filters": [
            ["name", "in", [
                "High Risk Cases",
                "Active Licenses",
                "Expired Licenses",
                "Licenses Under Renewal",
                "Completed This Month",
                "Overdue Compliances",
                "Due in Next 30 Days",
                "High Risk Compliance"
            ]]
        ]
    },
    {
        "dt": "Dashboard Chart",
        "filters": [
            ["name", "in", [
                "Liability Exposure (Sum)",
                "Open vs Closed Cases",
                "Upcoming Hearings",
                "Licenses Expiry Next 30 60 90 Days",
                "License Renewals Per Month",
                "Compliance Status",
                "Compliance by Authority",
                "Risk Level",
                "Compliance by Factory"
            ]]
        ]
    },
    {
        "dt": "Workspace",
        "filters": [
            ["name", "in", [
                "Quantbit Factory Compliance"
            ]]
        ]
    }
]



doc_events = {
    "Compliance Master": {
        "on_update": "quantbit_factory_compliance.quantbit_factory_compliance.doctype.compliance_master.compliance_master.on_update"
    },
    "License Master": {
        "on_update": "quantbit_factory_compliance.quantbit_factory_compliance.doctype.license.license.on_update"
    }
}


scheduler_events = {
    "daily": [
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.expire_license_frr",
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.create_compliance_task",
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.create_license_task",
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.overdue_status_compliance_task",
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.close_compliance_task_status",
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.close_license_task_status",
        "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.send_factory_regulatory_notifications"
    ]
}


# scheduler_events = {
#     "cron": {
#         "*/1 * * * *": [ 
#             "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.expire_license_frr",
#             "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.create_compliance_task",
#             "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.create_license_task",
#             "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.overdue_status_compliance_task",
#             "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.close_compliance_task_status",
#             "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.close_license_task_status",
#             # "quantbit_factory_compliance.quantbit_factory_compliance.schedulers.send_factory_regulatory_notifications"
#         ]
#     }
# }


