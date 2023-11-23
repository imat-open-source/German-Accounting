import frappe
from frappe.utils import flt


def set_tax_category(doc, method=None):
    if doc.country:
        tax_category = frappe.get_cached_value('Country', doc.country, 'tax_category')
        if tax_category:
            doc.tax_category = tax_category