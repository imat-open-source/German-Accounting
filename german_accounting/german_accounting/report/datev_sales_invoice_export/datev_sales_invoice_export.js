// Copyright (c) 2024, phamos.eu and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["DATEV Sales Invoice Export"] = {
	"filters": [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            "default": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
                "December"
            ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
        },
        {
            "fieldname": 'from_date',
            "label": __('From'),
            "fieldtype": 'Date',
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "60px"
        },
        {
            "fieldname": 'to_date',
            "label": __('To'),
            "fieldtype": 'Date',
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": 'unexported_sales_invoice',
            "label": __('Sales Invoice Exported'),
            "fieldtype": 'Date',
            "hidden": 1
        },
        {
            "fieldname": 'export_type',
            "label": __('Export Type'),
            "fieldtype": "Select",
            "default": "Sales Invoice CSV",
            "options": "\nSales Invoice CSV\nSales Invoice PDF\nDebtors CSV",
            "reqd": 1
        }
    ]
};
