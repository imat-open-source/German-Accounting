import frappe

def execute():
	fields_to_delete = [
		{
			"dt": "Quotation",
			"fieldname": "vat_id"
		},
		{
			"dt": "Sales Order",
			"fieldname": "vat_id"
		},
		{
			"dt": "Sales Invoice",
			"fieldname": "vat_id"
		},
	]
	for field in fields_to_delete:
		if frappe.db.exists("Custom Field", field):
			custom_field_name = frappe.db.get_value("Custom Field", dict(dt=field.get("dt"), fieldname=field.get("fieldname")))
			frappe.delete_doc("Custom Field", custom_field_name)
			frappe.clear_cache(doctype=field.get("dt"))