frappe.ui.form.on(cur_frm.doctype, {
	validate: function (cur_frm) {
		let row;
	    let goods = 0;
	    let services = 0;


        // Here we go through the item table and count the amounts for the two categories
	    for(row in cur_frm.doc.items)
	    {
	        if (cur_frm.doc.items[row].item_group === "Goods") {goods += cur_frm.doc.items[row].amount}
	        else if (cur_frm.doc.items[row].item_group === "Services") {services += cur_frm.doc.items[row].amount}   
	    }

        // test which amount is higher...
	    if (goods >= services) {cur_frm.set_value("item_category_by_amount","Goods")} else {cur_frm.set_value("item_category_by_amount","Services")}

        // case distinction for "vat_print_display"
	    if (cur_frm.doc.destination_selection === "Germany" && cur_frm.doc.item_category_by_amount === "Goods")
	        {cur_frm.set_value("vat_print_display","19% VAT")}

	    if (cur_frm.doc.destination_selection === "Germany" && cur_frm.doc.item_category_by_amount === "Services")
	        {cur_frm.set_value("vat_print_display","19% VAT")}

	    if (cur_frm.doc.destination_selection === "EU country (except Germany)" && cur_frm.doc.item_category_by_amount === "Goods")
	        {
	            if (cur_frm.doc.is_vat_id_applicable)
	            {cur_frm.set_value("vat_print_display","0% VAT, tax-free intra-community supply")}
	            else
	            {cur_frm.set_value("vat_print_display","19% VAT")}
	        }

	    if (cur_frm.doc.destination_selection === "EU country (except Germany)" && cur_frm.doc.item_category_by_amount === "Services")
	        {
	            if (cur_frm.doc.is_vat_id_applicable)
	            {cur_frm.set_value("vat_print_display","0% VAT, tax-free intra-community service (reverse charge procedure)")}
	            else
	            {cur_frm.set_value("vat_print_display","19% VAT")}
	        }

	    if (cur_frm.doc.destination_selection === "Non-EU country" && cur_frm.doc.item_category_by_amount === "Goods")
	        {cur_frm.set_value("vat_print_display","0% VAT, VAT-free export delivery")}

	    if (cur_frm.doc.destination_selection === "Non-EU country" && cur_frm.doc.item_category_by_amount === "Services")
	        {
	            if (cur_frm.doc.is_vat_id_applicable)
	            {cur_frm.set_value("vat_print_display","0% VAT, service non-taxable domestically")}
	            else
	            {cur_frm.set_value("vat_print_display","19% VAT")}
	        }
	}
})