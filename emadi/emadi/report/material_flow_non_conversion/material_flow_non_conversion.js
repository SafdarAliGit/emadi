
// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Material Flow Non Conversion"] = {
	"filters": [
		{
			"fieldname": "p",
			"label": "Waste %",
			"fieldtype": "Float",
			"default": 10
			},
		{
			"fieldname": "brand",
			"label": "Brand",
			"fieldtype": "Link",
			"options": "Brand",
			// "reqd": 1
		},
		// {
		// 	"fieldname": "customer",
		// 	"label": "Customer",
		// 	"fieldtype": "Link",
		// 	"options": "Customer",
		// 	// "reqd": 1
		// },
		{
			"fieldname": "yarn_count",
			"label": "Yarn Count Warp",
			"fieldtype": "Link",
			"options": "Item",
			// "reqd": 1,
			"get_query": function() {
				return {
					"filters": {
						"is_stock_item": 1,
						"item_group": ["in", ["Yarn", "Beam"]] // Use the "in" operator
					}
				};
			}
		},
		{
			"fieldname": "yarn_count_weft",
			"label": "Yarn Count Weft",
			"fieldtype": "Link",
			"options": "Item",
			// "reqd": 1,
			"get_query": function() {
				return {
					"filters": {
						"is_stock_item": 1,
						"item_group": "Yarn"
					}
				};
			}
		},
		{
			"fieldname": "fabric_item",
			"label": "Fabric Item",
			"fieldtype": "Link",
			"options": "Item",
			// "reqd": 1,
			"get_query": function() {
				return {
					"filters": {
						"is_stock_item": 1,
						"item_group": "Fabric"
					}
				};
			}
		}
	]
};
