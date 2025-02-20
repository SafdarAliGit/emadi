// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Weaving Contract', {
	refresh: function(frm) {
		frm.set_query('construction', function() {
			return {
				"filters": {
					"item_group": "Fabric"
				}
			}
		});
		frm.set_query('yarn_count','bom_items', function() {
			return {
				"filters": {
					"item_group": "Yarn"
				}
			}
		})

	},
	sizing_rate_per_meter: function(frm) {
		frm.set_value("total_charges_per_meter", flt(frm.doc.sizing_rate_per_meter) + flt(frm.doc.weaving_rate_per_meter));
	},
	weaving_rate_per_meter: function(frm) {
		frm.set_value("total_charges_per_meter", flt(frm.doc.sizing_rate_per_meter) + flt(frm.doc.weaving_rate_per_meter));
	}
});

frappe.ui.form.on('BOM Items', {
	consumption: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.model.set_value(d.doctype, d.name, "yarn_qty", frm.doc.fabric_qty * d.consumption);
		calculate_total(frm);
	},
	yarn_qty: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.model.set_value(d.doctype, d.name, "required_bags", d.yarn_qty / d.lbs_per_bag);
	},
	lbs_per_bag: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.model.set_value(d.doctype, d.name, "required_bags", d.yarn_qty / d.lbs_per_bag);
		calculate_total(frm);
	}
});


function calculate_total(frm) {
	let yarn_qty = 0;
	let required_bags = 0;
	let consumption = 0;
	$.each(frm.doc.bom_items || [], function (i, d) {
		yarn_qty += flt(d.yarn_qty);
		required_bags += flt(d.required_bags);
		consumption += flt(d.consumption);
	});
	frm.set_value("total_yarn", yarn_qty);
	frm.set_value("total_bags", required_bags);
	frm.set_value("total_consumption", consumption);
}