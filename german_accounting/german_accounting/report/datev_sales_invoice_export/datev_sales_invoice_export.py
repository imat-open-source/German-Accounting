# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cstr, today, now_datetime, get_first_day, get_last_day, format_date
from datetime import datetime
from collections import defaultdict
import json


@frappe.whitelist()
def execute(filters=None):
	if isinstance(filters, str):
		filters = json.loads(filters)
	filters = frappe._dict(filters or {})
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
	"""
		SELECT
			si.name as invoice_no, si.posting_date, si.is_return,si.cost_center, 
			si.tax_id, si.currency, si.grand_total, si.net_total as pdf_net_total,
			si.debit_to, si.custom_exported_on, co.code, ad.country, si.customer, 
			sii.income_account, sii.item_tax_rate
		FROM `tabSales Invoice` si, `tabSales Invoice Item` sii, `tabAddress` ad, `tabCountry` co
		WHERE si.docstatus=1 AND si.name = sii.parent AND si.customer_address=ad.name AND ad.country=co.name %s
	"""% conditions,filters, as_dict = 1)
	
	invoices_map = {}
	for entry in data:
		h_or_s = "S" if entry.get('is_return') else "H"
		grand_total = cstr(("%.2f" % flt(entry.grand_total))).replace(",","").replace(".","")
		invoices_map.setdefault(entry.get('invoice_no'), []).append({
			"posting_date": format_date(entry.get('posting_date'), "ddmm"),
			"pdf_posting_date": format_date(entry.get('posting_date'), "dd.mm.YYYY"),
			"cost_center": entry.get('cost_center').split("-")[0].replace(" ", "") if entry.get('cost_center') else "",
			"tax_id": entry.get('tax_id') if entry.get('tax_id') else "",
			"currency": entry.get('currency'),
			"grand_total": "{0}{1}".format(grand_total, h_or_s),
			"pdf_total_datev": entry.pdf_net_total,
			"pdf_total": entry.grand_total,
			"pdf_net_total": entry.pdf_net_total,
			"debit_to": entry.get('debit_to'),
			"item_tax_rate": entry.get('item_tax_rate'),
			"income_account": entry.get('income_account'),
			"custom_exported_on": entry.get('custom_exported_on'),
			"country": entry.code,
			"journal_text": entry.customer if entry.country == 'Germany' else entry.code + ", " + entry.customer,
			"customer": entry.customer,
			"dc": h_or_s
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
			merged_values['pdf_posting_date'] = entry['pdf_posting_date']
			merged_values['custom_exported_on'] = entry['custom_exported_on']
			merged_values['grand_total'] = entry['grand_total']
			merged_values['debit_to'] = entry['debit_to']
			merged_values['cost_center'] = entry['cost_center']
			merged_values['tax_id'] = entry['tax_id']
			merged_values['dc'] = entry['dc']
			merged_values['currency'] = entry['currency']
			merged_values['country'] = entry['country']
			merged_values['journal_text'] = entry['journal_text']
			merged_values['pdf_total_datev'] = entry['pdf_total_datev']
			merged_values['pdf_net_total'] = entry['pdf_net_total']
			merged_values['pdf_total'] = entry['pdf_total']
			merged_values['customer'] = entry['customer']

		merged_data[key] = merged_values

	data = []
	for inv_name, inv_data in merged_data.items():
		row = {}
		row['invoice_no'] = inv_name
		row['voucher_type'] = 'R'
		row.update(inv_data)
		if row.get('debit_to'):
			### Debitor No DATEV 
			deb_no_datev = row['debit_to'].split("-")[0].replace(" ", "")
			row['debit_to'] = deb_no_datev
			if len(deb_no_datev) < 9:
				n = 9 - len(deb_no_datev)
				zeros = '0' * n
				deb_no_datev += zeros
			# row['debit_to'] = deb_no_datev
			row['debitor_no_datev'] = deb_no_datev

		data.append(row)

	if filters.get("export_type") == "Debtors CSV":
		data = get_debtors_csv_data(data)

	return data

def get_debtors_csv_data(data):
	customers = list(set([d.get("customer") for d in data]))

	debtors_csv_data = frappe.db.sql(
	"""
		SELECT
			cust.tax_id, cust.name as customer, acc.account as debitor_no_datev
		FROM 
			`tabCustomer` cust
		LEFT JOIN
			`tabParty Account` acc ON cust.name = acc.parent
		WHERE 
			cust.name in (%s)
	"""% ", ".join(["%s"] * len(customers)), tuple(customers), as_dict=1)

	for d in debtors_csv_data:
		d['debitor_no_datev'] = d['debitor_no_datev'] if d.get("debitor_no_datev") else ""
		if d.get("debitor_no_datev"):
			debitor_no_datev = d['debitor_no_datev'].split("-")[0].replace(" ", "")
			if len(debitor_no_datev) < 9:
				n = 9 - len(debitor_no_datev)
				zeros = '0' * n
				debit_no_datev += zeros
			d['debitor_no_datev'] = debitor_no_datev

	return debtors_csv_data


def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		filters["month"] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
				"December"].index(filters.month) + 1
		conditions += "AND month(si.posting_date) = %(month)s"

	if filters.get("unexported_sales_invoice"):
		conditions += " AND coalesce(si.custom_exported_on, '') = '' "

	elif not filters.get("unexported_sales_invoice") and filters.get("exported_on"):
		conditions += " AND si.custom_exported_on = %(exported_on)s"

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
	else:
		if filters.get("month"):
			today = datetime.today().date()
			first_day = get_first_day(today.replace(month=filters.get("month")))
			last_day = get_last_day(today.replace(month=filters.get("month")))
			conditions += " AND si.posting_date BETWEEN '{0}' AND '{1}'".format(first_day, last_day)

	return conditions

def get_columns(filters):
	sales_inv_csv_columns = [
		{
			"label": _("grand_total"),
			"fieldtype": "Data",
			"fieldname": "grand_total",
			"custom_header": "amount",
			"width": 100
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space1",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _("debitor_no_datev"),
			"fieldtype": "Data",
			"fieldname": "debitor_no_datev",
			"custom_header": "customer",
			"width": 90
		},
		{
			"label": _("invoice_no"),
			"fieldtype": "Link",
			"fieldname": "invoice_no",
			"options": "Sales Invoice",
			"is_quoted_in_csv": 1,
			"custom_header": "invoice no.",
			"width": 170
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space2",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _("posting_date"),
			"fieldtype": "Data",
			"fieldname": "posting_date",
			"custom_header": "invoice date",
			"width": 100
		},
		{
			"label": _("income_account"),
			"fieldtype": "Data",
			"fieldname": "income_account",
			"custom_header": "G/L account",
			"width": 160
		},
		{
			"label": _("cost_center"),
			"fieldtype": "Data",
			"fieldname": "cost_center",
			"custom_header": "cost centre",
			"width": 120
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space3",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space4",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space5",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space6",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _("tax_id"),
			"fieldtype": "Data",
			"fieldname": "tax_id",
			"custom_header": "Vat-Id",
			"width": 110
		},
		{
			"label": _("item_tax_rate"),
			"fieldtype": "Data",
			"fieldname": "item_tax_rate",
			"custom_header": "Tax rate",
			"width": 120
		},
		{
			"label": _("currency"),
			"fieldtype": "Data",
			"fieldname": "currency",
			"custom_header": "currency",
			"is_quoted_in_csv": 1,
			"width": 110
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space6",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space7",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "col_space8",
			"custom_header": "",
			"width": 20
		},
		{
			"label": _(""),
			"fieldtype": "Data",
			"fieldname": "1_col",
			"custom_header": "",
			"one_col": True,
			"width": 160
		}
	]

	sales_inv_pdf_columns = [
		{
			"label": _("Voucher Type"),
			"fieldtype": "Data",
			"fieldname": "voucher_type",
			"custom_header": "Belegart",
			"width": 160
		},
		{
			"label": _("DC"),
			"fieldtype": "Data",
			"fieldname": "dc",
			"custom_header": "SH",
			"width": 160
		},
		{
			"label": _("Total"),
			"fieldtype": "Data",
			"fieldname": "pdf_total",
			"custom_header": "Betrag",
			"width": 160
		},
		{
			"label": _("Total DATEV"),
			"fieldtype": "Data",
			"fieldname": "pdf_total_datev",
			"custom_header": "Betrag DATEV",
			"width": 160
		},
		{
			"label": _("Income Account"),
			"fieldtype": "Data",
			"fieldname": "income_account",
			"custom_header": "Erlöskonto",
			"width": 160
		},
		{
			"label": _("Voucher No"),
			"fieldtype": "Data",
			"fieldname": "invoice_no",
			"custom_header": "Beleg Nr",
			"width": 160
		},
		{
			"label": _("Posting Date"),
			"fieldtype": "Data",
			"fieldname": "pdf_posting_date",
			"custom_header": "Buchungsdatum",
			"width": 160
		},
		{
			"label": _("Shortdate"),
			"fieldtype": "Data",
			"fieldname": "posting_date",
			"custom_header": "Kurzdatum",
			"width": 160
		},
		{
			"label": _("Debitor No"),
			"fieldtype": "Data",
			"fieldname": "debit_to",
			"custom_header": "Deb.-Nr.",
			"width": 160
		},
		{
			"label": _("Debitor No DATEV"),
			"fieldtype": "Data",
			"fieldname": "debitor_no_datev",
			"custom_header": "Deb.-Nr. Datev",
			"width": 160
		},
		{
			"label": _("Country"),
			"fieldtype": "Data",
			"fieldname": "country",
			"custom_header": "Land",
			"width": 160
		},
		{
			"label": _("Journal Text"),
			"fieldtype": "Data",
			"fieldname": "journal_text",
			"custom_header": "Buchtext",
			"width": 160
		},
		{
			"label": _("Tax Percentige"),
			"fieldtype": "Data",
			"fieldname": "item_tax_rate",
			"custom_header": "St.-satz",
			"width": 160
		},
		{
			"label": _("Currency"),
			"fieldtype": "Data",
			"fieldname": "currency",
			"custom_header": "Währung",
			"width": 160
		},
		{
			"label": _("Exportdate"),
			"fieldtype": "Data",
			"fieldname": "custom_exported_on",
			"custom_header": "Exportdatum",
			"width": 160
		},
	]

	debtors_csv_columns = [
		{
			"label": _("Debitor No DATEV"),
			"fieldtype": "Data",
			"fieldname": "debitor_no_datev",
			"custom_header": "Debitoren Nummer",
			"width": 160
		},
		{
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"fieldname": "customer",
			"custom_header": "Kundenname",
			"width": 160
		},
		{
			"label": _("Tax ID"),
			"fieldtype": "Data",
			"fieldname": "tax_id",
			"custom_header": "Tax ID",
			"width": 160
		}
	]

	if filters.get("export_type") == "Sales Invoice CSV":
		return sales_inv_csv_columns
	elif  filters.get("export_type") == "Sales Invoice PDF":
		return sales_inv_pdf_columns
	elif  filters.get("export_type") == "Debtors CSV":
		return debtors_csv_columns
	else:
		return []