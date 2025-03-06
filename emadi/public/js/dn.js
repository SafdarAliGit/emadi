frappe.ui.form.on('Delivery Note', {
    fabric_qty: function(frm) {
        if (frm.doc.fabric_qty) {
            $.each(frm.doc.items || [], function(index, row) {
                frappe.model.set_value(row.doctype, row.name, "qty", frm.doc.fabric_qty);
            });
            frm.refresh_field("items");

            $.each(frm.doc.bom_items_dn|| [], function(index, row) {
                frappe.model.set_value(row.doctype, row.name, "yarn_qty", frm.doc.fabric_qty * row.consumption);
            });
            frm.refresh_field("bom_items_dn");
        }
    }
});