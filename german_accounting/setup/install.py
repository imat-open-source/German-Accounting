import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
	create_custom_fields(get_custom_fields())


def before_uninstall():
	delete_custom_fields(get_custom_fields())


def delete_custom_fields(custom_fields):
	for doctype, fields in custom_fields.items():
		for field in fields:
			custom_field_name = frappe.db.get_value(
				"Custom Field", dict(dt=doctype, fieldname=field.get("fieldname"))
			)
			if custom_field_name:
				frappe.delete_doc("Custom Field", custom_field_name)

		frappe.clear_cache(doctype=doctype)


def get_custom_fields():
	custom_fields_transaction = [
		{
			"label": "IMAT Section",
			"fieldname": "imat_section",
			"fieldtype": "Section Break",
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Data",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "imat_section",
			"description": "This field will be filled by either 'Goods' or 'Services' depending on the result that is calculated in the item table."
		}
	]

	return {
		"Quotation": custom_fields_transaction,
		"Sales Order": custom_fields_transaction,
		"Sales Invoice": custom_fields_transaction
	}
