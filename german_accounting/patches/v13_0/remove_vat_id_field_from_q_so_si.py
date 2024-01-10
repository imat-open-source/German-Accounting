import frappe

def execute():
	# frappe.reload_doc("accounts", "doctype", "tax_category")
	# frappe.reload_doc("stock", "doctype", "item_manufacturer")

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