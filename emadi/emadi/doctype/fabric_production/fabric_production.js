// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fabric Production', {
	refresh: function(frm) {
		frm.set_query('yarn_count','fabric_production_item', function() {
			return {
				"filters": {
					"item_group": "Yarn"
				}
			}
		})
		frm.set_query('beam_item', function() {
			return {
				"filters": {
					"item_group": "Beam"
				}
			}
		})
		frm.set_query('weft_item', function() {
			return {
				"filters": {
					"item_group": "Yarn"
				}
			}
		})
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
