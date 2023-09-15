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
	return {
		"Quotation": [
            {
                "label": "Is VAT ID Applicable",
                "fieldname": "is_vat_id_applicable",
                "fieldtype": "Check",
                "insert_after": "items_section"
            },
            {
                "label": "Destination Selection",
                "fieldname": "destination_selection",
                "fieldtype": "Select",
                "options": "Germany\nEU country (except Germany)\nNon-EU country",
                "insert_after": "is_vat_id_applicable"
            },
            {
                "label": "Item Category By Amount",
                "fieldname": "item_category_by_amount",
                "fieldtype": "Data",
                "insert_after": "items",
				"hidden": 1
            },
            {
                "label": "VAT Print Display",
                "fieldname": "vat_print_display",
                "fieldtype": "Text",
                "insert_after": "item_category_by_amount"
            }
		],
		"Sales Order": [
            {
                "label": "Is VAT ID Applicable",
                "fieldname": "is_vat_id_applicable",
                "fieldtype": "Check",
                "insert_after": "items_section"
            },
            {
                "label": "Destination Selection",
                "fieldname": "destination_selection",
                "fieldtype": "Select",
                "options": "Germany\nEU country (except Germany)\nNon-EU country",
                "insert_after": "is_vat_id_applicable"
            },
            {
                "label": "Item Category By Amount",
                "fieldname": "item_category_by_amount",
                "fieldtype": "Data",
                "insert_after": "items",
				"hidden": 1
            },
            {
                "label": "VAT Print Display",
                "fieldname": "vat_print_display",
                "fieldtype": "Text",
                "insert_after": "item_category_by_amount"
            }
		],
		"Sales Invoice": [
            {
                "label": "Is VAT ID Applicable",
                "fieldname": "is_vat_id_applicable",
                "fieldtype": "Check",
                "insert_after": "scan_barcode"
            },
            {
                "label": "Destination Selection",
                "fieldname": "destination_selection",
                "fieldtype": "Select",
                "options": "Germany\nEU country (except Germany)\nNon-EU country",
                "insert_after": "is_vat_id_applicable"
            },
            {
                "label": "Item Category By Amount",
                "fieldname": "item_category_by_amount",
                "fieldtype": "Data",
                "insert_after": "items",
				"hidden": 1
            },
            {
                "label": "VAT Print Display",
                "fieldname": "vat_print_display",
                "fieldtype": "Text",
                "insert_after": "item_category_by_amount"
            }
		],
	}
