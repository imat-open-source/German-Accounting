frappe.ui.form.on("Address", {
	onload: function (frm) {
        frm.set_df_property('tax_category', 'reqd', 1);
        frm.add_fetch('country', 'tax_category', 'tax_category');
	},
});