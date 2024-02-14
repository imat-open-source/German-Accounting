// Copyright (c) 2024, phamos.eu and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["DATEV Sales Invoice"] = {
	"filters": [
        // {
        //     "fieldname": "customer",
		// 	"label": __("Customer"),
		// 	"fieldtype": "MultiSelectList",
		// 	get_data: function(txt) {
		// 		return frappe.db.get_link_options("Customer", txt);
		// 	}
        // },
        {
            fieldname: 'posting_date',
            label: __('Posting Date'),
            fieldtype: 'Date',
            default: frappe.datetime.get_today()
        }
    ]
};
