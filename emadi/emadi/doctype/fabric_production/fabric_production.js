// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fabric Production', {
	refresh: function(frm) {
        frm.set_query('target_warehouse', function() {
            return {
                "filters": [
					["is_group", "=", 0 ]
				]
            };
        });
        
		frm.set_query('yarn_count','fabric_production_item', function() {
			return {
				"filters": [
					["item_group", "in", ["Yarn","Beam"]]
				]
			}
		});
        frm.set_query('set_no', 'fabric_production_item', function(doc, cdt, cdn) {
			let child = locals[cdt][cdn];
			return {
				filters: {
					item: child.yarn_count
				}
			};
		});
	},
	quality: function(frm) {
        if (frm.doc.quality && frm.doc.qty) {
            frappe.call({
                method: "emadi.emadi.events.fetch_fabric_construction_items.fetch_fabric_construction_items",
                args: {
                    quality: frm.doc.quality,
                    qty: frm.doc.qty
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("fabric_production_item");
                        $.each(r.message, function(_, item) {
                            let row = frm.add_child("fabric_production_item");
                            row.for = item.for;
                            row.yarn_count = item.yarn_count;
                            row.consumption = item.consumption;
                            row.yarn_qty = item.yarn_qty;
                        });
                        frm.refresh_field("fabric_production_item");
                    }
                }
            });
        }
    },
    qty: function(frm) {
        // Recalculate when qty changes
        frm.trigger("quality");
    }
});

frappe.ui.form.on('Fabric Production Item', {
    
    warehouse: function(frm,cdt,cdn) {
        var row = locals[cdt][cdn];
        if (row.yarn_count && row.warehouse) {
            frappe.call({
                method: "emadi.emadi.events.fetch_current_stock.fetch_current_stock",
                args: {
                    item_code: row.yarn_count,
                    warehouse: row.warehouse,
                    set_no: row.set_no
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "available_qty", r.message || 0);
                    }
                }
            });
        }
    },
    yarn_count: function(frm) {
        // Recalculate when qty changes
        row.trigger("warehouse");
    }
})