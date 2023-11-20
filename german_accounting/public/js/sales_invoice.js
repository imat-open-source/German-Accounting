frappe.ui.form.on("Sales Invoice", {
	onload: function (frm) {
        frm.set_df_property('shipping_address_name', 'reqd', 1);
	},
});