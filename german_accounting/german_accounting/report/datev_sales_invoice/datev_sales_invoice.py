# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import today, now_datetime, get_first_day, get_last_day
from datetime import datetime
import json

@frappe.whitelist()
def execute(filters=None):
    if isinstance(filters, str):
        filters = json.loads(filters)
    filters = frappe._dict(filters or {})
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Voucher Type"),
            "fieldtype": "Data",
            "fieldname": "voucher_type",
            "width": 110
        },
        {
            "label": _("DC"),
            "fieldtype": "Data",
            "fieldname": "dc",
            "width": 50
        },
        {
            "label": _("Total"),
            "fieldtype": "Currency",
            "fieldname": "total",
            "width": 100
        },
        {
            "label": _("Total DATEV"),
            "fieldtype": "Data",
            "fieldname": "total_datev",
            "width": 110
        },
        {
            "label": _("Income Account"),
            "fieldtype": "Data",
            "fieldname": "income_account",
            # "options": "Account",
            "width": 130
        },
        {
            "label": _("Voucher No"),
            "fieldtype": "Link",
            "fieldname": "voucher_no",
            "options": "Sales Invoice",
            "width": 180
        },
        {
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "fieldname": "posting_date",
            "width": 110
        },
        {
            "label": _("Short Date"),
            "fieldtype": "Data",
            "fieldname": "short_date",
            "width": 110
        },
        {
            "label": _("Debitor No"),
            "fieldtype": "Data",
            "fieldname": "debit_to",
            # "options": "Account",
            "width": 120
        },
        {
            "label": _("Debitor No DATEV"),
            "fieldtype": "Data",
            "fieldname": "debit_to_datev",
            "width": 140
        },
        {
            "label": _("Country"),
            "fieldtype": "Link",
            "fieldname": "country",
            "options": "Country",
            "width": 80
        },
        {
            "label": _("Journal Text"),
            "fieldtype": "Small Text",
            "fieldname": "journal_text",
            "width": 150
        },
        {

            "label": _("Tax Percentage"),
            "fieldtype": "Data",
            "fieldname": "tax_percentage",
            "width": 130
        },
        {
            "label": _("Currency"),
            "fieldtype": "Link",
            "fieldname": "currency",
            "options": "Currency",
            "width": 90
        },
        {
            "label": _("Export Date"),
            "fieldtype": "Data",
            "fieldname": "export_date",
            "width": 180
        }
    ]

    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("posting_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("month"):
        filters["month"] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
                "December"].index(filters.month) + 1
        conditions += "AND month(si.posting_date) = %(month)s"
    
    if filters.get("exported_on"):
        exported_on = filters.get("exported_on")
        if filters.get("exported_on") == True:
            exported_on = now_datetime().strftime("%d-%m-%Y %H:%M:%S")
        conditions += " AND si.custom_exported_on = '{0}' ".format(exported_on)

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    else:
        if filters.get("month"):
            today = datetime.today().date()
            first_day = get_first_day(today.replace(month=filters.get("month")))
            last_day = get_last_day(today.replace(month=filters.get("month")))
            conditions += " AND si.posting_date BETWEEN '{0}' AND '{1}'".format(first_day, last_day)

    return conditions


def get_data(filters):
    data = []
    conditions = get_conditions(filters)
    res = frappe.db.sql(
        """ SELECT si.*, co.code, ad.country
            FROM `tabSales Invoice` si, `tabAddress` ad, `tabCountry` co
            WHERE si.docstatus!=2 AND si.customer_address=ad.name AND ad.country=co.name %s  """% conditions,filters, as_dict = 1)
    
    for d in res:
        line_item_details = frappe.db.sql(""" SELECT sii.income_account, ttd.tax_rate
                                            FROM `tabSales Invoice Item` sii, `tabItem Tax Template Detail` ttd
                                            WHERE sii.item_tax_template = ttd.parent """, as_dict = 1)
        income_account = ""
        tax_percentage = 0
        if len(line_item_details) != 0:
            income_account = line_item_details[0].income_account
            tax_percentage = line_item_details[0].tax_rate

        ### Debitor No DATEV 
        deb_no_datev = d.debit_to.split("-")[0].replace(" ", "")
        if len(deb_no_datev) < 9:
            n = 9 - len(deb_no_datev)
            zeros = '0' * n
            deb_no_datev += zeros
        # while len(deb_no_datev) <= 9:
        #     deb_no_datev += '0'

        
        row = {"voucher_type": "R", 
                "dc": "H" if d.is_return == 0 else "S", 
                "voucher_no": d.name, 
                "posting_date": d.posting_date, 
                "short_date": d.posting_date.strftime("%d%m"), 
                # "customer": d.customer, 
                "debit_to": d.debit_to.split("-")[0],
                "debit_to_datev": deb_no_datev,
                "income_account": income_account.split("-")[0],
                "country": d.code, 
                "currency": d.currency, 
                "journal_text": d.customer if d.country == 'Germany' else d.code + ", " + d.customer, 
                "export_date": d.custom_exported_on,
                "total": d.grand_total, 
                "total_datev": str(("%.2f" % d.grand_total)).replace(",","").replace(".",""), 
                "tax_percentage": tax_percentage}

        data.append(row)

    return data
