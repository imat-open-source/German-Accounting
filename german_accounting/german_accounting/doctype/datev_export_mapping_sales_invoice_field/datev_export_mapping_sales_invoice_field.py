# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class DATEVExportMappingSalesInvoiceField(Document):
	def autoname(self):
		self.name = self.field_name
