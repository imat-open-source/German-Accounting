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
            "fieldname": 'from_date',
            "label": __('From'),
            "fieldtype": 'Date',
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
        },
        {
            "fieldname": 'to_date',
            "label": __('To'),
            "fieldtype": 'Date',
            "default": frappe.datetime.get_today()
        }
    ]
};
