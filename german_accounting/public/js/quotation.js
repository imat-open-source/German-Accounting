frappe.ui.form.on("Quotation", {
	validate: function (frm) {
        frm.events.add_fetch_customer_type(frm)
	},

    quotation_to: function (frm) {
        frm.events.add_fetch_customer_type(frm)
    },

    party_name: function (frm) {
        frm.events.add_fetch_customer_type(frm)
    },

    add_fetch_customer_type: function (frm) {
        if (frm.doc.quotation_to)  {
            if (frm.doc.quotation_to === 'Customer' && frm.doc.party_name) {
                frm.add_fetch('party_name', 'customer_type', 'customer_type');
            } else if (frm.doc.quotation_to === 'Lead' && frm.doc.party_name) {
                frappe.db.get_value('Lead', frm.doc.party_name, 'organization_lead', function(value) {
                    debugger;
                    if (value['organization_lead'] === 1) {
                        frm.set_value('customer_type', 'Company')
                    } else {
                        frm.set_value('customer_type', 'Individual')
                    }
                });
            }
        }
	},
});