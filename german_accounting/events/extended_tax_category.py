import frappe
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of

def validate_tax_category_fields(doc, method=None):
    goods_amt_sum = 0.0
    services_amt_sum = 0.0

    def get_parent_and_descendants_list(item_group):
        item_groups = [item_group]
        descendants_item_group = get_descendants_of("Item Group", item_group)
        if descendants_item_group:
            item_groups = item_groups + descendants_item_group

        return item_groups

    goods_item_group = frappe.get_cached_value('German Accounting Settings', None, 'goods_item_group')
    service_item_group = frappe.get_cached_value('German Accounting Settings', None, 'service_item_group')
    if not goods_item_group:
        frappe.throw('Please set Goods Item Group in German Accounting Settings')

    if not service_item_group:
        frappe.throw('Please set Service Item Group in German Accounting Settings')

    # Here we go through the item table and count the amounts for the two categories
    for item in doc.get("items"):
        if item.item_group in get_parent_and_descendants_list(goods_item_group):
            goods_amt_sum += flt(item.amount)
        elif item.item_group in get_parent_and_descendants_list(service_item_group):
            services_amt_sum += flt(item.amount)

    # Test which amount is higher...
    if goods_amt_sum >= services_amt_sum:
        doc.item_group = goods_item_group
    else:
        doc.item_group = service_item_group