import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

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
	custom_fields_quotation = [
		{
			"label": "German Accounting",
			"fieldname": "german_accounting",
			"fieldtype": "Section Break",
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Data",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "german_accounting",
			"description": "This field will be filled by either 'Goods' or 'Services' depending on the result that is calculated in the item table."
		},
		{
			"label": "Tax Id",
			"fieldname": "tax_id",
			"fieldtype": "Data",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "item_group",
			"description": "This can be a validation in the backround that will check if the `vatid` field in Customer/Address is set."
		},
		{
			"label": "Customer Type",
			"fieldname": "customer_type",
			"fieldtype": "Select",
			"options": "\nCompany\nIndividual",
			"default": "",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "tax_id",
		}
	]

	custom_fields_so = [
		{
			"label": "German Accounting",
			"fieldname": "german_accounting",
			"fieldtype": "Section Break",
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Data",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "german_accounting",
			"description": "This field will be filled by either 'Goods' or 'Services' depending on the result that is calculated in the item table."
		},
		{
			"label": "Customer Type",
			"fieldname": "customer_type",
			"fieldtype": "Select",
			"options": "\nCompany\nIndividual",
			"default": "",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "german_accounting",
		}
	]

	custom_fields_si = [
		{
			"label": "German Accounting",
			"fieldname": "german_accounting",
			"fieldtype": "Section Break",
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Data",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "german_accounting",
			"description": "This field will be filled by either 'Goods' or 'Services' depending on the result that is calculated in the item table."
		},
		{
			"label": "Customer Type",
			"fieldname": "customer_type",
			"fieldtype": "Select",
			"options": "\nCompany\nIndividual",
			"default": "",
			"read_only": 1,
			"translatable": 0,
			"insert_after": "german_accounting",
		},
		{
			"label": "Exported On",
			"fieldname": "custom_exported_on",
			"fieldtype": "Data",
			"no_copy": 1,
			"hidden": 0,
			"read_only": 1,
			"translatable": 0,
			"insert_after": "customer_type",
		}
	]

	custom_fields_country = [
		{
			"label": "German Accounting",
			"fieldname": "german_accounting",
			"fieldtype": "Section Break",
		},
		{
			"label": "Tax Category",
			"fieldname": "tax_category",
			"fieldtype": "Link",
			"options": "Tax Category",
			"insert_after": "german_accounting",
		},
		{
			"fieldtype": "Section Break",
			"fieldname": "other_fields_sb",
		},
	]

	custom_fields_item_group = [
		{
			"label": "German Accounting Tax Defaults",
			"fieldname": "german_accounting_taxes",
			"fieldtype": "Table",
			"options": "German Accounting Tax Defaults",
			"insert_after": "taxes"
		}	
	]

	custom_fields_customer = [
		{
			"label": "German Accounting",
			"fieldname": "german_accounting_section",
			"fieldtype": "Section Break",
			"insert_after": None,
		},
		{
			"label": "Billing Address",
			"fieldname": "billing_address",
			"fieldtype": "Link",
			"description": "This represents the standard billing address used for the export for DATEV debtors file.",
			"insert_after": "german_accounting_section",
			"options": "Address"
		}
	]

	return {
		"Quotation": custom_fields_quotation,
		"Sales Order": custom_fields_so,
		"Item Group": custom_fields_item_group,
		"Sales Invoice": custom_fields_si,
		"Country": custom_fields_country,
		"Customer": custom_fields_customer
	}
