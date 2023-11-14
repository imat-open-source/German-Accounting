import frappe
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of


def validate_tax_category_fields(doc, method=None):
    goods_amt_sum = 0.0
    services_amt_sum = 0.0

    def get_parent_and_descendants_item_group_list(item_group):
        item_groups = [item_group]
        descendants_item_group = get_descendants_of("Item Group", item_group)
        return item_groups + descendants_item_group if descendants_item_group else item_groups

    german_accounting_settings = frappe.get_cached_doc('German Accounting Settings')

    if not german_accounting_settings.goods_item_group:
        frappe.throw('Please set Goods Item Group in German Accounting Settings')

    if not german_accounting_settings.service_item_group:
        frappe.throw('Please set Service Item Group in German Accounting Settings')

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

    else:
        doc.item_group = german_accounting_settings.service_item_group
