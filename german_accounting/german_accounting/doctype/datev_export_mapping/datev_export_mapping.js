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
					let html_format = "<p>No print format setup!</p>"
					await frappe.db.get_single_value("German Accounting Settings", "include_header_in_csv").then((value) => {
						if (value) {
							include_header_in_csv = true;
						}
					});

					await frappe.call({
						method: "frappe.desk.query_report.get_script",
						args: {
							report_name: "DATEV Sales Invoice Export",
						},
						callback: function (r) {
							html_format = r.message.html_format;
						},
					});

					// frappe.dom.freeze()

					frappe.call({
						method: "german_accounting.german_accounting.report.datev_sales_invoice_export.datev_sales_invoice_export.execute",
						args: {
							filters: {
								'month': data.month,
								'csv_pdf': 'CSV',
								'unexported_sales_invoice': true
							}
						},
						async: false,
						callback: function(r, rt) {
							if (r.message) {
								let csv = r.message;
								let csv_columns = csv[0];
								let csv_rows = csv[1];
								var result = [];
								if (csv_rows.length == 0) {
									frappe.throw("No data found!")
								}
								let sales_invoices = csv_rows.map(row => row.invoice_no);

								if (include_header_in_csv) {
									let field_mapping_table = csv_columns.map(column => column.custom_header);
									result.push(field_mapping_table);
								}

								csv_rows.forEach(function (row) {
									let csv_row = [];
								
									csv_columns.forEach(function (mapping) {
										let mapping_label = mapping.label;
										let one_col = mapping.one_col;
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
												csv_row.push("1");
											} else {
												csv_row.push("");
											}
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
											let datev_export_log_name = r.message.name;
											let datev_exported_on = r.message.exported_on;
											frappe.dom.unfreeze();
											// CSV
											// Create a Blob containing the CSV data
											const csv = createCsv(result, ";");
											const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });

											upload_file(blob, datev_export_log_name, '.csv', 'csv');

											frappe.call({
												method: "german_accounting.german_accounting.report.datev_sales_invoice_export.datev_sales_invoice_export.execute",
												args: {
													filters: {
														'month': data.month,
														'csv_pdf': 'PDF',
														'exported_on': datev_exported_on,
														'unexported_sales_invoice': false
													}
												},
												callback: function (r) {
													let pdf = r.message;
													let pdf_columns = pdf[0];
													let pdf_rows = pdf[1];

													// PDF
													const content = frappe.render_template(html_format, {
														title: __("DATEV Sales Invoice"),
														subtitle: "filters_html",
														filters: {
															'month': data.month
														},
														data: pdf_rows,
														columns: pdf_columns,
													});

													const html = frappe.render_template('print_template', {
														title: __("DATEV Sales Invoice"),
														content: content,
														base_url: frappe.urllib.get_base_url(),
														print_css: frappe.boot.print_css,
														print_settings: {},
														landscape: false,
														columns: pdf_columns,
														lang: frappe.boot.lang,
														layout_direction: frappe.utils.is_rtl() ? "rtl" : "ltr",
													});

													//Create a form to place the HTML content
													var formData1 = new FormData();

													//Push the HTML content into an element
													formData1.append("html", html);
													// if (opts.orientation) {
													// 	formData1.append("orientation", opts.orientation);
													// }
													var blob1 = new Blob([], { type: "text/xml" });
													formData1.append("blob", blob1);

													// Make a fetch request
													fetch("/api/method/frappe.utils.print_format.report_to_pdf", {
														method: "POST",
														headers: {
															"X-Frappe-CSRF-Token": frappe.csrf_token
														},
														body: formData1
													})
													.then(response => {
														if (!response.ok) {
															frappe.throw("Report PDF Generation Failed!");
														}
														return response.arrayBuffer(); // Get the response as an ArrayBuffer
													})
													.then(arrayBuffer => {
														// Convert the ArrayBuffer to a Blob
														var blob = new Blob([arrayBuffer], { type: "application/pdf" });
														upload_file(blob, datev_export_log_name, '.pdf', 'pdf');

													})
													.catch(error => {
														// Handle any errors
														console.error("There was a problem with the fetch operation:", error);
													});
												},
											});

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

const upload_file = (blob, datev_export_log_name, format, field) => {
	// Create a FormData object
	const formData = new FormData();

	// Append the Blob as a file to the FormData object
	formData.append('file', blob, 'report-' + datev_export_log_name + format);
	formData.append('folder', "Home/Attachments");						
	formData.append('doctype', 'DATEV Export Log');
	formData.append('docname', datev_export_log_name);
	formData.append('fieldname', field);
	formData.append('is_private', '1');											

	fetch('/api/method/upload_file', {
		headers: {
			'X-Frappe-CSRF-Token': frappe.csrf_token
		},
		method: 'POST',
		body: formData
	}).then(res => res.json()).then(data => {			
		if (data.message){
			frappe.db.set_value("DATEV Export Log", datev_export_log_name, field, data.message.file_url);	
		}
	})
};
  
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
  