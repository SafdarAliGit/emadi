// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Weaving Contract', {
	refresh: function(frm) {

		if (frm.doc.docstatus == 1 && frm.doc.custom_status == "Close") {
			frm.add_custom_button(__('OPEN'), function() {
				frappe.confirm(
					'Are you sure you want to OPEN this weaving contract?',
					function() {
						// OK pressed
						frappe.call({
							method: "emadi.emadi.events.open_weaving_contract.open_weaving_contract",
							args: {
								weaving_contract: frm.doc.name
							},
							callback: function(r) {
								if (!r.exc) {
									frappe.model.sync(r.message);
									frappe.set_route("Form", r.message.doctype, r.message.name);
								}
							}
						});
					},
					function() {
						// Cancel pressed - do nothing
					}
				);
			}).css('background-color', 'green')
			  .css('color', '#ffffff')
			  .css('font-weight', 'bold');
		}

		if (frm.doc.docstatus == 1 && frm.doc.custom_status == "Open") {
			frm.add_custom_button(__('CLOSE'), function() {
				frappe.confirm(
					'Are you sure you want to CLOSE this weaving contract?',
					function() {
						// OK pressed
						frappe.call({
							method: "emadi.emadi.events.close_weaving_contract.close_weaving_contract",
							args: {
								weaving_contract: frm.doc.name
							},
							callback: function(r) {
								if (!r.exc) {
									frappe.model.sync(r.message);
									frappe.set_route("Form", r.message.doctype, r.message.name);
								}
							}
						});
					},
					function() {
						// Cancel pressed - do nothing
					}
				);
			}).css('background-color', 'red')
			  .css('color', '#ffffff')
			  .css('font-weight', 'bold');
		}
		

		if (frm.doc.docstatus == 1 && frm.doc.custom_status == "Open") {
            frm.add_custom_button(__('Create DO'), function() {
                frappe.call({
                    method: "emadi.emadi.events.create_dn.create_dn",
                    args: {
                        weaving_contract: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
							frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
                    }
                });
            }).css('background-color', '#06599c').css('color', '#ffffff','font-weight','bold');
		}
		
		if (frm.doc.docstatus == 1 && frm.doc.custom_status == "Open") {
            frm.add_custom_button(__('Stock Entry'), function() {
                frappe.call({
                    method: "emadi.emadi.events.create_stock_entry_from_weaving_contract.create_stock_entry_from_weaving_contract",
                    args: {
                        weaving_contract: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
							frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
                    }
                });
            }).css('background-color', '#ff9800').css('color', '#ffffff','font-weight','bold');
		}

		if (frm.doc.docstatus == 1 && frm.doc.custom_status == "Open") {
            frm.add_custom_button(__('Sizing Program'), function() {
                frappe.call({
                    method: "emadi.emadi.events.create_sizing_program_from_weaving_contract.create_sizing_program_from_weaving_contract",
                    args: {
                        weaving_contract: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
							frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
                    }
                });
            }).css('background-color', '#2490EF').css('color', '#ffffff','font-weight','bold');
		}
		
		if (frm.doc.docstatus == 1 && frm.doc.custom_status == "Open") {
            frm.add_custom_button(__('Material Request'), function() {
                frappe.call({
                    method: "emadi.emadi.events.create_material_request_from_weaving_contract.create_material_request_from_weaving_contract",
                    args: {
                        weaving_contract: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
							frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
                    }
                });
            }).css('background-color', '#00A884').css('color', '#ffffff','font-weight','bold');
		}
		
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
					"item_group": ["in", ["Yarn", "Fabric"]]
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