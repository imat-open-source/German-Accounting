// Copyright (c) 2024, phamos.eu and contributors
// For license information, please see license.txt

frappe.ui.form.on('DATEV Export Mapping', {
	refresh: function(frm) {
		frm.add_custom_button(__('Show Report'), function () {
			frappe.set_route('query-report', 'DATEV Sales Invoice', {})
		});

		// csv download
		frm.add_custom_button(__('Create DATEV Export Log'), function () {

			let d = new frappe.ui.Dialog({
				title: __("Select Month"),
				fields: [
					{
						"fieldname": "month",
						"label": __("Month"),
						"fieldtype": "Select",
						"options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
						"default": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
							"December"
						][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
						"reqd": 1
					}
				],
				primary_action: async function() {
					let data = d.get_values();
					let include_header_in_csv = false;
					await frappe.db.get_single_value("German Accounting Settings", "include_header_in_csv").then((value) => {
						if (value) {
							include_header_in_csv = true;
						}
					});

					// frappe.dom.freeze()

					frappe.call({
						method: "german_accounting.german_accounting.report.datev_sales_invoice_export.datev_sales_invoice_export.execute",
						args: {
							filters: {
								'month': data.month,
								'unexported_sales_invoice': true
							}
						},
						async: false,
						callback: function(r, rt) {
							if (r.message) {
								let columns = r.message[0];
								let rows = r.message[1];
								var result = [];
								if (rows.length == 0) {
									frappe.throw("No data found!")
								}
								let sales_invoices = rows.map(row => row.invoice_no);

								if (include_header_in_csv) {
									let field_mapping_table = columns.map(column => column.custom_header);
									result.push(field_mapping_table);
								}

								rows.forEach(function (row) {
									let csv_row = [];
								
									columns.forEach(function (mapping) {
										let mapping_label = mapping.label;
										let one_col = mapping.one_col;
										// debugger;
										if ((mapping_label !== "") && mapping_label in row) {
											if (mapping.is_quoted_in_csv) {
												csv_row.push('"'+row[mapping_label]+'"');
											}
											else {
												csv_row.push(row[mapping_label]);
											}
										}
										else {
											if (one_col) {
												debugger;
												csv_row.push("1");
											} else {
												csv_row.push("");
											}
											// csv_row.push([""]);
										}
									});
								
									result.push(csv_row);
								});

								frappe.call({
									"method": "german_accounting.german_accounting.doctype.datev_export_mapping.datev_export_mapping.create_log",
									args:{
										"month": data.month,
										"datev_exp_map": frm.doc.name,
										"sales_invoices": sales_invoices
									},
									async: false,
									freeze: true,
									freeze_message: __("Creating Log"),
									callback: function(r){
										if (r.message) {
											let datev_export_log_name = r.message;
											frappe.dom.unfreeze();
											// Create a Blob containing the CSV data
											const csv = createCsv(result, ";");
											const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });

											// Create a FormData object
											const formData = new FormData();

											// Append the Blob as a file to the FormData object
											formData.append('file', blob, 'report-' + datev_export_log_name +'.csv');
											formData.append('folder', "Home/Attachments");						
											formData.append('doctype', 'DATEV Export Log');
											formData.append('docname', datev_export_log_name);
											formData.append('fieldname', 'csv');
											formData.append('is_private', '1');											

											fetch('/api/method/upload_file', {
												headers: {
													'X-Frappe-CSRF-Token': frappe.csrf_token
												},
												method: 'POST',
												body: formData
											}).then(res => res.json()).then(data => {			
												if (data.message){
													frappe.db.set_value("DATEV Export Log", datev_export_log_name, "csv", data.message.file_url);	
												}
											})
										}
									}
								})
							}
						}
					})
					d.hide();
				},
				primary_action_label: __("Submit")
			});
			d.show();
			
		});
		
	},
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

const createCsv = (rows, delimiter) => {
let returnStr = "";
rows.forEach(row => {
	row.forEach(field => {
		returnStr += field + delimiter;
	});
	returnStr += "\r\n";
});
	return returnStr.trimEnd();
};
  