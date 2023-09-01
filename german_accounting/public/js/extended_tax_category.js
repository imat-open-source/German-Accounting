frappe.ui.form.on(cur_frm.doctype, {
	validate: function (cur_frm) {
		    var row;
	    var liefbetrag = 0;
	    var sonstbetrag = 0;


        // Here we go through the item table and count the amounts for the two categories
	    for(row in cur_frm.doc.items)
	    {
	        if (cur_frm.doc.items[row].item_group == "Lieferung") {liefbetrag += cur_frm.doc.items[row].qty * cur_frm.doc.items[row].price_list_rate}
	        if (cur_frm.doc.items[row].item_group == "Sonstige Leistung") {sonstbetrag += cur_frm.doc.items[row].qty * cur_frm.doc.items[row].price_list_rate}   
	    }

        // test which amount is higher...
	    if (liefbetrag >= sonstbetrag) {cur_frm.set_value("artikelkategorie_nach_amount","Lieferung")} else {cur_frm.set_value("artikelkategorie_nach_amount","Sonstige Leistung")}

        // case distinction for "text_fuer_druck"
	    if (cur_frm.doc.auswahl_ziel == "Inland" && cur_frm.doc.artikelkategorie_nach_amount == "Lieferung")
	        {cur_frm.set_value("text_fuer_druck","19% Ust")}

	    if (cur_frm.doc.auswahl_ziel == "Inland" && cur_frm.doc.artikelkategorie_nach_amount == "Sonstige Leistung")
	        {cur_frm.set_value("text_fuer_druck","19% Ust")}

	    if (cur_frm.doc.auswahl_ziel == "EU-Ausland" && cur_frm.doc.artikelkategorie_nach_amount == "Lieferung")
	        {
	            if (cur_frm.doc.ust_id == "Ja")
	            {cur_frm.set_value("text_fuer_druck","0% Ust  –  Steuerfreie innergemeinschaftliche Lieferung")}
	            else
	            {cur_frm.set_value("text_fuer_druck","19% Ust")}
	        }

	    if (cur_frm.doc.auswahl_ziel == "EU-Ausland" && cur_frm.doc.artikelkategorie_nach_amount == "Sonstige Leistung")
	        {
	            if (cur_frm.doc.ust_id == "Ja")
	            {cur_frm.set_value("text_fuer_druck","0% Ust  –  Steuerfreie innergemeinschaftliche Lieferung (Reverse-Charge-Verfahren)")}
	            else
	            {cur_frm.set_value("text_fuer_druck","19% Ust")}
	        }

	    if (cur_frm.doc.auswahl_ziel == "Drittland" && cur_frm.doc.artikelkategorie_nach_amount == "Lieferung")
	        {cur_frm.set_value("text_fuer_druck","0% Ust  –  Umsatzsteuerfreie Ausfuhrlieferung")}

	    if (cur_frm.doc.auswahl_ziel == "Drittland" && cur_frm.doc.artikelkategorie_nach_amount == "Sonstige Leistung")
	        {
	            if (cur_frm.doc.ust_id == "Ja")
	            {cur_frm.set_value("text_fuer_druck","0% Ust  –  Im Inland nicht steuerbare Leistung")}
	            else
	            {cur_frm.set_value("text_fuer_druck","19% Ust")}
	        }
	}
})