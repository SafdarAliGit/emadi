// Copyright (c) 2025, Safdar Ali and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Material Flow"] = {
	"filters": [
		{
			"fieldname": "brand",
			"label": "Brand",
			"fieldtype": "Link",
			"options": "Brand",
			// "reqd": 1
		},
		{
			"fieldname": "yarn_count",
			"label": "Yarn Count",
			"fieldtype": "Link",
			// "reqd": 1,
			"get_query": function() {
				return {
					"filters": {
						"maintain_stock": 1
					}
				};
			}
		}
	]
};
