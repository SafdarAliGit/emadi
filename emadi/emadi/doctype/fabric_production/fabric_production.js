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
        frm.set_query('set_no','fabric_production_item', function() {
            return {
                "filters": [
                    ["item", "=", frm.doc.yarn_count]
                ]
            }
        })
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
    
    warehouse(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        // Only proceed if essential fields are present
       
        frm.call({
            method: 'emadi.emadi.events.fetch_current_stock.fetch_current_stock',
            args: {
                item_code: row.yarn_count,
                warehouse: row.warehouse,
                set_no: row.set_no
            },
            callback: ({ message }) => {
                const available = message?.current_stock || 0;
                const rate = message?.rate || 0;
                const yarnQty = row.yarn_qty || 0;
                const amount = yarnQty * rate;

                frappe.model.set_value(cdt, cdn, 'available_qty', available);
                frappe.model.set_value(cdt, cdn, 'valuation_rate', rate);
                frappe.model.set_value(cdt, cdn, 'amount', amount);

                recalculate_rate(frm);
            },
            error: err => {
                frappe.msgprint({
                    title: __('Stock Fetch Error'),
                    message: __('Could not load stock data for row {0}', [row.idx]),
                    indicator: 'red'
                });
            }
        });
    },
    yarn_count: function(frm) {
        // Recalculate when qty changes
        row.trigger("warehouse");
    }
})


// Shared logic to total up amounts and calculate rate
function recalculate_rate(frm) {
    const items = frm.doc.fabric_production_item || [];
    let total_amount = 0;
   items.forEach(element => {
        total_amount += element.amount;
   });
    frm.set_value('total_amount', total_amount);
    const qty = flt(frm.doc.qty);
    let avg_rate = 0;
    if (qty > 0) {
      avg_rate = flt(total_amount) / qty;
      frm.set_value('finish_rate', avg_rate);
    }
    
    if (frm.doc.valuation_type === 0 && avg_rate <= 0) {
      frappe.throw(__('Rate must be greater than zero'));
    }
  }
  
  