import frappe
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