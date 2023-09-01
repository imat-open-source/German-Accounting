import frappe

def validate_tax_category_fields(doc, method=None):
    liefbetrag = 0
    sonstbetrag = 0

    # Here we go through the item table and count the amounts for the two categories
    for item in doc.get("items"):
        if item.item_group == "Lieferung":
            liefbetrag += item.qty * item.price_list_rate
        elif item.item_group == "Sonstige Leistung":
            sonstbetrag += item.qty * item.price_list_rate

    # Test which amount is higher...
    if liefbetrag >= sonstbetrag:
        doc.artikelkategorie_nach_amount = "Lieferung"
    else:
        doc.artikelkategorie_nach_amount = "Sonstige Leistung"

    # Case distinction for "text_fuer_druck"
    if doc.auswahl_ziel == "Inland" and doc.artikelkategorie_nach_amount == "Lieferung":
        doc.text_fuer_druck = "19% Ust"

    if doc.auswahl_ziel == "Inland" and doc.artikelkategorie_nach_amount == "Sonstige Leistung":
        doc.text_fuer_druck = "19% Ust"

    if doc.auswahl_ziel == "EU-Ausland" and doc.artikelkategorie_nach_amount == "Lieferung":
        if doc.ust_id == "Ja":
            doc.text_fuer_druck = "0% Ust  –  Steuerfreie innergemeinschaftliche Lieferung"
        else:
            doc.text_fuer_druck = "19% Ust"

    if doc.auswahl_ziel == "EU-Ausland" and doc.artikelkategorie_nach_amount == "Sonstige Leistung":
        if doc.ust_id == "Ja":
            doc.text_fuer_druck = "0% Ust  –  Steuerfreie innergemeinschaftliche Lieferung (Reverse-Charge-Verfahren)"
        else:
            doc.text_fuer_druck = "19% Ust"

    if doc.auswahl_ziel == "Drittland" and doc.artikelkategorie_nach_amount == "Lieferung":
        doc.text_fuer_druck = "0% Ust  –  Umsatzsteuerfreie Ausfuhrlieferung"

    if doc.auswahl_ziel == "Drittland" and doc.artikelkategorie_nach_amount == "Sonstige Leistung":
        if doc.ust_id == "Ja":
            doc.text_fuer_druck = "0% Ust  –  Im Inland nicht steuerbare Leistung"
        else:
            doc.text_fuer_druck = "19% Ust"
