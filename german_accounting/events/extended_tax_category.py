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
            item_groups + descendants_item_group

        return item_groups

    # Here we go through the item table and count the amounts for the two categories
    for item in doc.get("items"):
        if item.item_group in get_parent_and_descendants_list("Goods"):
            goods_amt_sum += flt(item.amount)
        elif item.item_group in get_parent_and_descendants_list("Services"):
            services_amt_sum += flt(item.amount)

    # Test which amount is higher...
    if goods_amt_sum >= services_amt_sum:
        item_category_by_amount = "Goods"
    else:
        item_category_by_amount = "Services"

    # Case distinction for "vat_print_display"
    if doc.destination_selection == "Germany" and item_category_by_amount == "Goods":
        doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "Germany" and item_category_by_amount == "Services":
        doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "EU country (except Germany)" and item_category_by_amount == "Goods":
        if doc.is_vat_id_applicable:
            doc.vat_print_display = "0% VAT, tax-free intra-community supply"
        else:
            doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "EU country (except Germany)" and item_category_by_amount == "Services":
        if doc.is_vat_id_applicable:
            doc.vat_print_display = "0% VAT, tax-free intra-community service (reverse charge procedure)"
        else:
            doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "Non-EU country" and item_category_by_amount == "Goods":
        doc.vat_print_display = "0% VAT, VAT-free export delivery "

    if doc.destination_selection == "Non-EU country" and item_category_by_amount == "Services":
        if doc.is_vat_id_applicable:
            doc.vat_print_display = "0% VAT, service non-taxable domestically"
        else:
            doc.vat_print_display = "19% VAT"
