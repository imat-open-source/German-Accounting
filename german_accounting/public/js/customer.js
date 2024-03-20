frappe.ui.form.on('Customer', {
    onload(frm) {
        // FILTER BILLING ADDRESS WITH RESPECTIVE CONDITIONS
        frm.set_query('billing_address', function () {
            return {
                query: 'frappe.contacts.doctype.address.address.address_query',
                filters: {
                    is_primary_address: 1,
                    link_doctype: frm.doc.doctype,
                    link_name: frm.doc.name
                }
            };
        });
    }
})