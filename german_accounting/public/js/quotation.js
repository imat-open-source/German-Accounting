frappe.ui.form.on("Quotation", {
	onload: function (frm) {
        frm.set_df_property('tax_category', 'reqd', 1);
	},
});