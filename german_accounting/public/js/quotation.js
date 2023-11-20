frappe.ui.form.on("Quotation", {
	onload: function (frm) {
        frm.set_df_property('shipping_address_name', 'reqd', 1);
	},
});