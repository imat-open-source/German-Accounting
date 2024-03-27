# Copyright (c) 2024, phamos.eu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime
from datetime import datetime, date


class DATEVExportMappingTemplate(Document):
	def autoname(self):
		self.name = "DATEV-Export-" + self.month + "-" + str(date.today().year)

	def validate(self):
		now = datetime.now()
		self.exported_on =  now_datetime().strftime("%d-%m-%Y %H:%M:%S")
