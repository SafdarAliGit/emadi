

frappe.query_reports["Material Flow Conversion"] = {
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
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			// "reqd": 1
		},
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
						"item_group": ["in", ["Yarn", "Beam"]]
					}
				};
			}
		},
		{
			"fieldname": "warp_opening",
			"label": "Warp Opening",
			"fieldtype": "Float",
			"default": 0
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
			"fieldname": "weft_opening",
			"label": "Weft Opening",
			"fieldtype": "Float",
			"default": 0
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
		},
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}

	]
};
