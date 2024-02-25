# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from datetime import date 

class DATEVExportMappingTemplate(Document):
	def autoname(self):
		self.name = "DATEV-Export-" + self.month + "-" + str(date.today().year)
