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
							filters: {'month': data.month}
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
									// row = row.toString().replace(",",";")

									result.push(row)
								}
							}
						}
					})
					
					result = arrayToCsvFile(result, ";", "DATEV SI Report.csv");
					
					// frappe.tools.downloadify(result, null, "DATEV SI Report");

					create_log(data.month, frm.doc.name, result)

					// var t = frappe.urllib.get_full_url(`/api/method/frappe.utils.print_format.download_pdf?
					// 		doctype=${frm.doc.doctype}
					// 		&name=${frm.doc.name}
					// 		&format=standard
					// 		&lang=en`)
					// 		console.log(t)
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


function create_log(month, datev_ex_map, result){
	frappe.call({
		"method": "german_accounting.german_accounting.doctype.datev_export_mapping.datev_export_mapping.create_log",
		args:{
			"month": month,
			"datev_exp_map": datev_ex_map,
			"csvData": result
		},
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