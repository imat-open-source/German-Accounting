// Copyright (c) 2024, phamos.eu and contributors
// For license information, please see license.txt

frappe.ui.form.on('DATEV Export Mapping Template', {
	refresh: function(frm) {
		frm.set_query('datev_export_mapping', function(doc) {
			return {
				filters: {
					"is_active": 1
				}
			};
		});

		frm.add_custom_button(__('Show Report'), function () {
			frappe.set_route('query-report', 'DATEV Sales Invoice', {})
		}, __('Actions'));

		// csv download
		frm.add_custom_button(__('Download Report'), function () {
			var child = []
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "DATEV Export Mapping",
					filters: {},
					fields: ["*"]
				},
				async: false,
				callback: function(t){
					child.push(t.message.field_mapping_table)
				}
			})
			var cus_column_headers = []
			var si_field_id = []
			if(child.length > 0){
				child[0].forEach((c) => {
					cus_column_headers.push(c.customer_field_id);
					si_field_id.push(c.sales_invoice_field_id)
				});
			}
			
			var result = []
			result.push(si_field_id)
			
			frappe.call({
				method: "german_accounting.german_accounting.report.datev_sales_invoice.datev_sales_invoice.execute",
				args: {
					filters: {'month': frm.doc.month}
				},
				async: false,
				callback: function(r, rt) {
					if (r.message) {
						for(var i in r.message[1]){
							var row = []
							for(var si in si_field_id){
								if(si_field_id[si] in r.message[1][i]){
									row.push(r.message[1][i][si_field_id[si]])
								}
								if(si_field_id[si] == ""){
									row.push([" "])
								}
							}
							result.push(row)
						}
					}
				}
			})

			frappe.tools.downloadify(result, null, "DATEV SI Report");

			// var t = frappe.urllib.get_full_url(`/api/method/frappe.utils.print_format.download_pdf?
			// 		doctype=${frm.doc.doctype}
			// 		&name=${frm.doc.name}
			// 		&format=standard
			// 		&lang=en`)
			// 		console.log(t)
		}, __('Actions'));
	}
});
