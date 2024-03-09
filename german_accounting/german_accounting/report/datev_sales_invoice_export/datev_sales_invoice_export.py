# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cstr, format_date
from collections import defaultdict
import json


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
	"""
		SELECT
			si.name as invoice_no, si.posting_date, si.is_return,
			si.cost_center, si.tax_id, si.currency, si.total, si.debit_to,
			sii.income_account, sii.item_tax_rate
		FROM `tabSales Invoice` si, `tabSales Invoice Item` sii
		WHERE si.docstatus!=2 AND si.name = sii.parent %s
	"""% conditions,filters, as_dict = 1)
	
	invoices_map = {}
	for entry in data:
		h_or_s = "S" if entry.get('is_return') else "H"
		invoices_map.setdefault(entry.get('invoice_no'), []).append({
			"posting_date": format_date(entry.get('posting_date'), "ddmm"),
			"cost_center": entry.get('cost_center').split("-")[0].replace(" ", "") if entry.get('cost_center') else "",
			"tax_id": entry.get('tax_id'),
			"currency": entry.get('currency'),
			"total": "{0}{1}".format(str(("%.2f" % flt(entry.total))).replace(",","").replace(".",""),h_or_s),
			"debit_to": entry.get('debit_to'),
			"item_tax_rate": entry.get('item_tax_rate'),
			"income_account": entry.get('income_account')
		})
	
	merged_data = {}
	for key, values in invoices_map.items():
		merged_values = {}
		income_accounts = set()
		item_tax_rates = set()

		for entry in values:
			income_account = entry['income_account']
			item_tax_rate = entry['item_tax_rate']
			if len(values) == 1 or (income_account in income_accounts):
				income_account = income_account.split("-")[0].replace(" ", "")
				merged_values['income_account'] = income_account

			else:
				income_accounts.add(income_account)
				merged_values['income_account'] = 'multiple income accounts'

			if len(values) == 1 or item_tax_rate in item_tax_rates:
				item_tax_rate = json.loads(item_tax_rate)
				item_tax_rate = sum(value for value in item_tax_rate.values())
				merged_values['item_tax_rate'] = flt(item_tax_rate)

			else:
				item_tax_rates.add(item_tax_rate)
				merged_values['item_tax_rate'] = 'multiple tax rates'

			merged_values['posting_date'] = entry['posting_date']
			merged_values['total'] = entry['total']
			merged_values['debit_to'] = entry['debit_to']
			merged_values['cost_center'] = entry['cost_center']
			merged_values['tax_id'] = entry['tax_id']
			merged_values['currency'] = entry['currency']

		merged_data[key] = merged_values

	data = []
	for inv_name, inv_data in dict(merged_data).items():
		row = {}
		row['invoice_no'] = inv_name
		row.update(inv_data)
		row['debit_to'] = row['debit_to'].split("-")[0].replace(" ", "")
		data.append(row)

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("posting_date"):
		conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
	
	return conditions

def get_columns():
	columns = [
		{
			"label": _("total"),
			"fieldtype": "Data",
			"fieldname": "total",
			"width": 100
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space1",
			"width": 20
		},
		{
			"label": _("debit_to"),
			"fieldtype": "Data",
			"fieldname": "debit_to",
			# "options": "Account",
			"width": 80
		},
		{
			"label": _("invoice_no"),
			"fieldtype": "Link",
			"fieldname": "invoice_no",
			"options": "Sales Invoice",
			"width": 170
		},
		{
			"label": _("posting_date"),
			"fieldtype": "Data",
			"fieldname": "posting_date",
			"width": 100
		},
		{
			"label": _("G/L account"),
			"fieldtype": "Data",
			"fieldname": "income_account",
			"width": 160
		},
		{
			"label": _("cost_center"),
			"fieldtype": "Data",
			"fieldname": "cost_center",
			# "options": "Account",
			"width": 120
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space2",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space3",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space4",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space5",
			"width": 20
		},
		{
			"label": _("tax_id"),
			"fieldtype": "Data",
			"fieldname": "tax_id",
			"width": 110
		},
		{
			"label": _("tax_rate"),
			"fieldtype": "Data",
			"fieldname": "item_tax_rate",
			"width": 120
		},
		{
			"label": _("currency"),
			"fieldtype": "Data",
			"fieldname": "currency",
			"width": 110
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space6",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space7",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space8",
			"width": 20
		},
		{
			"label": _("1"),
			"fieldtype": "Data",
			"fieldname": "1",
			"width": 110
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space9",
			"width": 20
		},
	]

	return columns
