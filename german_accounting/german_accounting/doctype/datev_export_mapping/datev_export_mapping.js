// Copyright (c) 2024, phamos.eu and contributors
// For license information, please see license.txt

frappe.ui.form.on('DATEV Export Mapping', {
	refresh: function(frm) {
		frm.add_custom_button(__('Show Report'), function () {
			frappe.set_route('query-report', 'DATEV Sales Invoice', {})
		}, __('Actions'));

		// csv download
		frm.add_custom_button(__('Download Report'), function () {

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
						"reqd": 1,
					}
				],
				primary_action: function() {
					const data = d.get_values();
					// create_log(data.month, frm.doc.name)

					// csv export
					var child = []
					var csv_result = []
					var pdf_result = []
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
					
					csv_result.push(si_field_id)

					var filters = {'month': data.month,
					'exported_on': true
				}
					
					frappe.call({
						method: "german_accounting.german_accounting.report.datev_sales_invoice.datev_sales_invoice.execute",
						args: {
							filters: filters
						},
						async: false,
						callback: function(r, rt) {
							if (r.message) {
								pdf_result.push(r.message)
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
									// row = row.toString().replace(",",";")

									csv_result.push(row)
								}
							}
						}
					})

					// arrayToCsvFile(csv_result, ";", "DATEV SI Report.csv");

					// upload csv data

					const blob = new Blob([csv_result], { type: 'text/csv;charset=utf-8,' })
					const objUrl = URL.createObjectURL(blob)
					console.log(objUrl)
					let imagefile = new FormData();					
						imagefile.append('doctype',frm.doc.doctype);
						imagefile.append('docname', frm.doc.name);											
						// imagefile.append('folder', "Home/");						
						imagefile.append('file', objUrl);

						fetch('/api/method/upload_file', {
							headers: {
								'X-Frappe-CSRF-Token': frappe.csrf_token
							},
							method: 'POST',
							body: imagefile
						})
						.then(res => 
							res.json())
						.then(data => {
							console.log(data)
						})


					// pdf export
					// var report_doc = []
					// frappe.db.get_doc("Report", "DATEV Sales Invoice")
					// .then((doc) => {
					// 	report_doc.push(doc)
					// });
					// const columns = pdf_result[0];
					// const pdf_data = pdf_result[1];

					// const filters_html = get_filters_html_for_print(filters);
					// const content = frappe.render_template("print_grid", {
					// 	title: __("DATEV Sales Invoice"),
					// 	subtitle: filters_html,
					// 	filters: filters,
					// 	data: pdf_data,
					// 	original_data: pdf_data,
					// 	columns: columns,
					// 	report: report_doc[0],
					// });
					
					// const print_settings = {"orientation": "Landscape", "with_letter_head": 0, "pick_columns": 0}
					// const html = frappe.render_template('print_template', {
					// 	title: __("DATEV Sales Invoice"),
					// 	content: content,
					// 	base_url: frappe.urllib.get_base_url(),
					// 	print_css: frappe.boot.print_css,
					// 	print_settings: print_settings,
					// 	landscape: 1,
					// 	columns: si_field_id,
					// 	lang: frappe.boot.lang,
					// 	layout_direction: frappe.utils.is_rtl() ? "rtl" : "ltr",
					// 	// can_use_smaller_font: this.report_doc.is_standard === "Yes" && custom_format ? 0 : 1,
					// });
					// console.log(content)
					// print_settings.report_name = "DATEV SALES INVOICE_"+ data.month + "_" + new Date().getFullYear() + ".pdf";
					// frappe.render_pdf(html, print_settings);
					
					
					// frappe.tools.downloadify(result, null, "DATEV SI Report");

					d.hide();
				},
				primary_action_label: __("Submit")
			});
			d.show();
			
		}, __('Actions'));
		
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


function create_log(month, datev_ex_map){
	frappe.call({
		"method": "german_accounting.german_accounting.doctype.datev_export_mapping.datev_export_mapping.create_log",
		args:{
			"month": month,
			"datev_exp_map": datev_ex_map,
			// "csvData": result
		},
		async: false,
		callback: function(r){
			
		}
	})
}

const arrayToCsvFile = (dataArray, delimiter, filename) => {
	const csv = createCsv(dataArray, delimiter);
	return exportCsvToFile(csv, filename, delimiter);
  };
  
  const createCsv = (rows, delimiter) => {
	let returnStr = "";
	rows.forEach(row => {
	  row.forEach(field => {
		returnStr += field + delimiter;
	  });
	  returnStr += "\r\n";
	});
	return returnStr;
  };
  
  const exportCsvToFile = (csvData, filename, delimiter) => {
	// FIXED: Comma instead of semicolon
	csvData = "data:text/csv;charset=utf-8," + csvData;
	const encodedUri = encodeURI(csvData);
	// Trick to set filename
	const link = document.createElement("a");
	link.setAttribute("href", encodedUri);
	link.setAttribute("download", filename);
	document.body.appendChild(link); // Required for Firefox(?)
	link.click();
	return csvData
  };

function get_filters_html_for_print(applied_filters) {
	return Object.keys(applied_filters)
		.map((fieldname) => {
			const docfield = get_filter(applied_filters, fieldname);
			const value = applied_filters[fieldname];
			return `<h6>${__(docfield.label)}: ${frappe.format(value, docfield)}</h6>`;
		})
		.join("");
}

function get_filter(applied_filters, fieldname) {
	var report_filters = [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            "default": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
                "December"
            ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
        },
        {
            "fieldname": 'from_date',
            "label": __('From'),
            "fieldtype": 'Date',
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "60px"
        },
        {
            "fieldname": 'to_date',
            "label": __('To'),
            "fieldtype": 'Date',
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": 'exported_on',
            "label": __('Exported On'),
            "fieldtype": 'Data',
            "hidden": 1
            // "default": frappe.datetime.get_today()
        }
    ]
	const field = (report_filters || []).find((f) => f.fieldname === fieldname);
	if (!field) {
		console.warn(`[Query Report] Invalid filter: ${fieldname}`);
	}
	return field;
}