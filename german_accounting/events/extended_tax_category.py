import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of


def validate_tax_category_fields(doc, method=None):
    goods_amt_sum = 0.0
    services_amt_sum = 0.0

    set_customer_type(doc)

    def get_parent_and_descendants_item_group_list(item_group):
        item_groups = [item_group]
        descendants_item_group = get_descendants_of("Item Group", item_group)
        return item_groups + descendants_item_group if descendants_item_group else item_groups

    german_accounting_settings = frappe.get_cached_doc('German Accounting Settings')

    if not german_accounting_settings.goods_item_group:
        frappe.throw('Please set Goods Item Group in German Accounting Settings')

    if not german_accounting_settings.service_item_group:
        frappe.throw('Please set Service Item Group in German Accounting Settings')

    if not german_accounting_settings.good_or_service_selection:
        frappe.throw('Please set Goods or Service Selection in German Accounting Settings')

    goods_item_group_list = get_parent_and_descendants_item_group_list(german_accounting_settings.goods_item_group)
    services_item_group_list = get_parent_and_descendants_item_group_list(german_accounting_settings.service_item_group)
    # Here we go through the item table and count the amounts for the two categories
    for item in doc.get("items"):
        if item.item_group in goods_item_group_list:
            goods_amt_sum += flt(item.amount)
        elif item.item_group in services_item_group_list:
            services_amt_sum += flt(item.amount)

    if goods_amt_sum > services_amt_sum:
        doc.item_group = german_accounting_settings.goods_item_group

    elif goods_amt_sum == services_amt_sum:
        good_or_service_selection = frappe.scrub(german_accounting_settings.good_or_service_selection)
        doc.item_group = german_accounting_settings.get(good_or_service_selection)

    else:
        doc.item_group = german_accounting_settings.service_item_group

    setting_tax_defaults(doc)


def setting_tax_defaults(doc):
    track_logs = frappe.db.get_single_value("German Accounting Settings", "track_logs")
    if doc.doctype == 'Quotation' and doc.quotation_to == 'Customer' and doc.party_name:
        doc.tax_id = frappe.get_cached_value("Customer", doc.party_name, "tax_id")

    if doc.item_group and doc.tax_category:
        is_vat_applicable = True if doc.tax_id else False
        filters = {
            'parent': doc.item_group, 
            'parenttype': 'Item Group',
            'tax_category': doc.tax_category, 
            'customer_type': doc.customer_type,
            'is_vat_applicable': is_vat_applicable
        }
        if frappe.db.exists('German Accounting Tax Defaults', filters):
            item_tax_template = frappe.get_cached_doc('German Accounting Tax Defaults', filters)
            if track_logs:
                frappe.msgprint(item_tax_template.item_tax_template)
            for item in doc.items:
                if item_tax_template.item_tax_template:
                    item.item_tax_template = item_tax_template.item_tax_template

                if doc.doctype == "Sales Invoice":
                    if item_tax_template.income_account:
                        item.income_account = item_tax_template.income_account
            
            if item_tax_template.sales_taxes_and_charges_template:
                doc.taxes_and_charges = item_tax_template.sales_taxes_and_charges_template
                doc.taxes = []

            doc.run_method("set_missing_values")
            doc.run_method("calculate_taxes_and_totals")
        else:
            for item in doc.items:
                if doc.doctype == "Sales Invoice":
                    item.income_account = ""
                
                item.item_tax_template = ""

            doc.taxes = []
            doc.taxes_and_charges = ""
            doc.run_method("set_missing_values")
            doc.run_method("calculate_taxes_and_totals")
            frappe.msgprint(_("This case is not reflected in the table (German Accounting Tax Defaults) in {0}. Please check the fields tax_category, customer_type, is_vat_applicable and add your combination to the table.").format(frappe.get_desk_link("Item Group", doc.item_group)))

def set_customer_type(doc):
    if doc.doctype == 'Quotation':
        if doc.quotation_to:
            if doc.quotation_to == 'Customer' and doc.party_name:
                doc.customer_type = frappe.get_cached_value('Customer', doc.party_name, 'customer_type')
            
            elif doc.quotation_to == 'Lead' and doc.party_name:
                organization_lead = frappe.get_cached_value('Lead', doc.party_name, 'organization_lead')
                if organization_lead:
                    doc.customer_type = 'Company'
                else:
                    doc.customer_type = 'Individual'
    elif doc.doctype in ['Sales Order', 'Sales Invoice']:
        doc.customer_type = frappe.get_cached_value('Customer', doc.customer, 'customer_type')
