// Copyright (c) 2024, phamos.eu and contributors
// For license information, please see license.txt

frappe.ui.form.on('DATEV Export Mapping', {
	// refresh: function(frm) {
	// 	frm.add_custom_button(__('Show Report'), function () {
	// 		frappe.set_route('query-report', 'DATEV Sales Invoice', {})
	// 	}, __('Actions'));
	// 	frm.add_custom_button(__('Download Report'), function () {
	// 		var child = frm.doc.field_mapping_table
	// 		var cus_column_headers = []
	// 		var si_field_id = []
	// 		child.forEach((c) => {
	// 			cus_column_headers.push(c.customer_field_id);
	// 			si_field_id.push(c.sales_invoice_field_id)
	// 		});
			
	// 		var result = []
	// 		result.push(si_field_id)
	// 		frappe.call({
	// 			method: "german_accounting.german_accounting.report.datev_sales_invoice.datev_sales_invoice.execute",
	// 			args: {
	// 				// filters: filters
	// 			},
	// 			async: false,
	// 			callback: function(r, rt) {
	// 				if (r.message) {
	// 					// console.log(r.message)
	// 					for(var i in r.message[1]){
	// 						var row = []
	// 						for(var si in si_field_id){
	// 							if(si_field_id[si] in r.message[1][i]){
	// 								row.push(r.message[1][i][si_field_id[si]])
	// 							}
	// 							if(si_field_id[si] == ""){
	// 								row.push([" "])
	// 							}
	// 						}
	// 						result.push(row)
	// 					}
	// 				}
	// 			}
	// 		})
	// 		// const column_row = si_field_id.reduce((acc, col) => {
	// 		// 	if (!col.hidden) {
	// 		// 		acc.push(__(col.label));
	// 		// 	}
	// 		// 	return acc;
	// 		// }, []);
	// 		// const out = [column_row].concat(result);
	// 		frappe.tools.downloadify(result, null, "DATEV SI Report");
	// 	}, __('Actions'));
	// },
	onload: function(frm){
		var df = frappe.meta.get_docfield("DATEV Export Mapping Table","sales_invoice_field_id", frm.doc.name);
		df.options = get_si_field_options();
		frm.refresh_field("field_mapping_table");
	}
});

frappe.ui.form.on('DATEV Export Mapping Table', {
	is_empty_column: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		var reqd_val = 0
		if(row.is_empty_column == 1){
			reqd_val = 1
			frappe.model.set_value(row.doctype, row.name, "sales_invoice_field_id", "");
			frappe.model.set_value(row.doctype, row.name, "customer_field_id", "");
		}
	}
});

function get_si_field_options() {
	let options = [];
	frappe.db.get_list(
		"DocField", {filters:{"parent": "Sales Invoice","parenttype": "Doctype", "fieldname": ["not like", ("section_break%", "column_break%")]}, fields:["fieldname"], order_by: "creation", limit: 500}
	).then((res) => {
		// console.log(res)
		res.forEach((field) => {
			options.push(field.fieldname);
		});
	});
	return options;
}
