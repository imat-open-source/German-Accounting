# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import today, now_datetime
from datetime import datetime


def execute(filters=None):
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
            "width": 150
        },
        {
            "label": _("DC"),
            "fieldtype": "Data",
            "fieldname": "dc",
            "width": 50
        },
        {
            "label": _("Total"),
            "fieldtype": "Data",
            "fieldname": "total",
            "width": 100
        },
        {
            "label": _("Total DATEV"),
            "fieldtype": "Data",
            "fieldname": "total_datev",
            "width": 100
        },
        {
            "label": _("Income Account"),
            "fieldtype": "Link",
            "fieldname": "income_account",
            "options": "Account",
            "width": 250
        },
        {
            "label": _("Voucher No"),
            "fieldtype": "Link",
            "fieldname": "voucher_no",
            "options": "Sales Invoice",
            "width": 200
        },
        {
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "fieldname": "posting_date",
            "width": 150
        },
        {
            "label": _("Shortdate"),
            "fieldtype": "Data",
            "fieldname": "short_date",
            "width": 150
        },
        {
            "label": _("Debitor No"),
            "fieldtype": "Link",
            "fieldname": "debit_to",
            "options": "Account",
            "width": 250
        },
        {
            "label": _("Debitor No DATEV"),
            "fieldtype": "Data",
            "fieldname": "debit_to_datev",
            "width": 250
        },
        {
            "label": _("Country"),
            "fieldtype": "Link",
            "fieldname": "country",
            "options": "Country",
            "width": 100
        },
        {
            "label": _("Journal Text"),
            "fieldtype": "Small Text",
            "fieldname": "journal_text",
            "width": 200
        },
        {

            "label": _("Tax Percentage"),
            "fieldtype": "Data",
            "fieldname": "tax_percentage",
            "width": 150
        },
        {
            "label": _("Currency"),
            "fieldtype": "Link",
            "fieldname": "currency",
            "options": "Currency",
            "width": 100
        },
        {
            "label": _("Export Date"),
            "fieldtype": "Data",
            "fieldname": "export_date",
            "width": 250
        }
    ]

    return columns


def get_conditions(filters):
    conditions = ""
    # if filters.get("customer"):
    #     conditions += " AND si.customer IN %(customer)s"
    if filters.get("posting_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    return conditions


def get_data(filters):

    data = []
    conditions = get_conditions(filters)
    res = frappe.db.sql(
        """ SELECT si.name, si.posting_date, si.customer, si.debit_to, si.currency, si.grand_total, si.is_return, si.remarks, co.code
            FROM `tabSales Invoice` si, `tabAddress` ad, `tabCountry` co
            WHERE si.shipping_address_name=ad.name AND ad.country=co.name %s  """% conditions,filters, as_dict = 1)

    for d in res:
        line_item_details = frappe.db.sql(""" SELECT sii.income_account, ttd.tax_rate
                                            FROM `tabSales Invoice Item` sii, `tabItem Tax Template Detail` ttd
                                            WHERE sii.item_tax_template = ttd.parent """, as_dict = 1)
        income_account = ""
        tax_percentage = 0
        if len(line_item_details) != 0:
            income_account = line_item_details[0].income_account
            tax_percentage = line_item_details[0].tax_rate
        
        row = {"voucher_type": "R", 
                "dc": "H" if d.is_return == 0 else "S", 
                "voucher_no": d.name, 
                "posting_date": d.posting_date, 
                "short_date": d.posting_date.strftime("%d%m"), 
                "customer": d.customer, 
                "debit_to": d.debit_to.split("-")[0], 
                "income_account": income_account.split("-")[0],
                "country": d.code, 
                "currency": d.currency, 
                "journal_text": d.remarks, 
                "export_date": now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
                "total": str("%.2f" % d.grand_total), 
                "total_datev": str(("%.2f" % d.grand_total)).replace(",","").replace(".",""), 
                "tax_percentage": tax_percentage}

        data.append(row)

    return data
