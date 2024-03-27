# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form, get_url,formatdate,get_first_day, getdate, today, now_datetime
from datetime import datetime, date
from frappe import _
import requests
import time

class DATEVExportMapping(Document):
	def validate(self):
		tab = self.field_mapping_table
		for t in self.field_mapping_table:
			if t.is_empty_column == 1 and not t.description:
				frappe.throw("Please add Description on row "+ str(t.idx))

		# active record validation
		if self.is_active == 1 and frappe.db.exists(self.doctype, {"is_active": 1, "name": ["!=", self.name]}):
			active_rec = frappe.db.get_value(self.doctype, {"is_active": 1, "name": ["!=", self.name]}, "name")
			frappe.throw("Only one active record can be created at a time, Already there is a active record "+ get_link_to_form(self.doctype, active_rec))


@frappe.whitelist()
def create_log(month, datev_exp_map, sales_invoices=[]):
	if sales_invoices and not isinstance(sales_invoices, list):
		sales_invoices = frappe.parse_json(sales_invoices)

	exported_on = now_datetime().strftime("%d-%m-%Y %H:%M:%S")
	log_doc = frappe.new_doc("DATEV Export Log")
	log_doc.update({
		"month": month,
		"exported_on": exported_on,
		"datev_export_mapping": datev_exp_map,
		"year": str(date.today().year)
	})
	log_doc.save(ignore_permissions=True)
	
	# update exported on in SI
	for si in sales_invoices:
		frappe.db.set_value("Sales Invoice", si, "custom_exported_on", exported_on)
		
	frappe.msgprint(_("A DATEV Export Log "+get_link_to_form("DATEV Export Log", log_doc.name) + " has been created for "+ month +" month containing a *.csv and *.pdf that can be downloaded"))
	# time.sleep(5)
	return log_doc
