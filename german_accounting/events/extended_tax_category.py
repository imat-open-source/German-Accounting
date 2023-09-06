import frappe

def validate_tax_category_fields(doc, method=None):
    goods = 0
    services = 0

    # Here we go through the item table and count the amounts for the two categories
    for item in doc.get("items"):
        if item.item_group == "Goods":
            goods += item.qty * item.price_list_rate
        elif item.item_group == "Services":
            services += item.qty * item.price_list_rate

    # Test which amount is higher...
    if goods >= services:
        doc.item_category_by_amount = "Goods"
    else:
        doc.item_category_by_amount = "Services"

    # Case distinction for "vat_print_display"
    if doc.destination_selection == "Germany" and doc.item_category_by_amount == "Goods":
        doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "Germany" and doc.item_category_by_amount == "Services":
        doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "EU country (except Germany)" and doc.item_category_by_amount == "Goods":
        if doc.vat_id == "Yes":
            doc.vat_print_display = "0% VAT, tax-free intra-community supply"
        else:
            doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "EU country (except Germany)" and doc.item_category_by_amount == "Services":
        if doc.vat_id == "Yes":
            doc.vat_print_display = "0% VAT, tax-free intra-community service (reverse charge procedure)"
        else:
            doc.vat_print_display = "19% VAT"

    if doc.destination_selection == "Non-EU country" and doc.item_category_by_amount == "Goods":
        doc.vat_print_display = "0% VAT, VAT-free export delivery "

    if doc.destination_selection == "Non-EU country" and doc.item_category_by_amount == "Services":
        if doc.vat_id == "Yes":
            doc.vat_print_display = "0% VAT, service non-taxable domestically"
        else:
            doc.vat_print_display = "19% VAT"
