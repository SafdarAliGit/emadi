// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Weaving Stock Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
			"reqd": 1
		},
		{
			"fieldname": "brand",
			"label": "Brand",
			"fieldtype": "Link",
			"options": "Brand",
			"reqd": 0
		},
		{
			"fieldname": "item_code",	
			"label": "Yarn Item",
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 0,
			"get_query": function() {
				return {
					"filters": {
						"item_group": "Yarn"
					}
				};
			}
		}
	]
};
