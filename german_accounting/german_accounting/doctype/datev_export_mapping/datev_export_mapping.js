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
					// frappe.dom.freeze()

					let delimiter = ";";
					let datev_export_filters = {};
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

					datev_export_filters = {
						'month': data.month,
						'export_type': 'Sales Invoice CSV',
						'unexported_sales_invoice': true
					}
					let datev_export_csv = await get_datev_export_data(datev_export_filters);
					if (datev_export_csv.message) {
						datev_export_csv = datev_export_csv.message;
						let csv_columns = datev_export_csv[0];
						let csv_rows = datev_export_csv[1];
						let sales_invoices = csv_rows.map(row => row.invoice_no);
						if (csv_rows.length == 0) {
							frappe.throw("No data found!")
						}

						let datev_export_log = await create_datev_export_log(data.month, frm.doc.name, sales_invoices);
						let datev_export_log_name = datev_export_log.message.name;
						let datev_exported_on = datev_export_log.message.exported_on;

						let csv_blob = create_csv_blob(csv_rows, csv_columns, include_header_in_csv, delimiter);
						let filename = datev_export_log_name + '-sales-invoice.csv';
						await upload_file(csv_blob, datev_export_log_name, filename, 'sales_invoice_csv');

						datev_export_filters = {
							'month': data.month,
							'export_type': 'Sales Invoice PDF',
							'unexported_sales_invoice': false,
							'exported_on': datev_exported_on,
						}
						let datev_export_pdf = await get_datev_export_data(datev_export_filters);
						if (datev_export_pdf.message) {
							datev_export_pdf = datev_export_pdf.message;
							let pdf_columns = datev_export_pdf[0];
							let pdf_rows = datev_export_pdf[1];
							await create_and_upload_pdf(data.month, pdf_columns, pdf_rows, html_format, datev_export_log_name);
						}
					}
					// frappe.dom.unfreeze();
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

const get_datev_export_data = (filters) => {
	return frappe.call({
		method: "german_accounting.german_accounting.report.datev_sales_invoice_export.datev_sales_invoice_export.execute",
		args: {
			filters: filters
		},
		callback: function (r) {
			return r.message;
		},
	});
}

const create_datev_export_log = (month, datev_exp_map, sales_invoices) => {
	return frappe.call({
		"method": "german_accounting.german_accounting.doctype.datev_export_mapping.datev_export_mapping.create_log",
		args:{
			"month": month,
			"datev_exp_map": datev_exp_map,
			"sales_invoices": sales_invoices
		},
		callback: function (r) {
			return r.message;
		},
	});
}

const create_csv_blob = (csv_rows, csv_columns, include_header_in_csv, delimiter) => {
	var csv_data = [];
	let csv_str = "";
	if (include_header_in_csv) {
		let field_mapping_table = csv_columns.map(column => column.custom_header);
		csv_data.push(field_mapping_table);
	}

	csv_rows.forEach(function (row) {
		let csv_row = [];
		csv_columns.forEach(function (mapping) {
			let mapping_label = mapping.fieldname;
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
		csv_data.push(csv_row);
	});

	csv_data.forEach(row => {
		row.forEach(field => {
			csv_str += field + delimiter;
		});
		csv_str += "\r\n";
	});

	csv_str = csv_str.trimEnd();
	let csv_blob = new Blob([csv_str], { type: 'text/csv;charset=utf-8' });
	return csv_blob
}

const create_and_upload_pdf = (month, pdf_columns, pdf_rows, html_format, datev_export_log_name) => {
	const content = frappe.render_template(html_format, {
		title: __("DATEV Sales Invoice"),
		subtitle: "filters_html",
		filters: {
			'month': month
		},
		data: pdf_rows
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
	var formData = new FormData();

	//Push the HTML content into an element
	formData.append("html", html);
	// if (opts.orientation) {
	// 	formData1.append("orientation", opts.orientation);
	// }
	var blob = new Blob([], { type: "text/xml" });
	formData.append("blob", blob);

	// Make a fetch request
	fetch("/api/method/frappe.utils.print_format.report_to_pdf", {
		method: "POST",
		headers: {
			"X-Frappe-CSRF-Token": frappe.csrf_token
		},
		body: formData
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
		let filename = datev_export_log_name + '-sales-invoice.pdf';
		upload_file(blob, datev_export_log_name, filename, 'sales_invoice_pdf');

	})
	.catch(error => {
		// Handle any errors
		console.error("There was a problem with the fetch operation:", error);
	});
}

const upload_file = (blob, datev_export_log_name, filename, field) => {
	// Create a FormData object
	const formData = new FormData();

	// Append the Blob as a file to the FormData object
	formData.append('file', blob, filename);
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