# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form

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
