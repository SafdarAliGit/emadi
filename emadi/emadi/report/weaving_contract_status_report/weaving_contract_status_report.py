
import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"label": "Contract No", "fieldname": "contract", "fieldtype": "Link", "options": "Weaving Contract", "width": 120},
        {"label": "Weaver", "fieldname": "weaver", "fieldtype": "Link", "options": "Customer", "width": 120},
        {"label": "Construction", "fieldname": "construction", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": "Fabric Qty", "fieldname": "fabric_qty", "fieldtype": "Float", "width": 100},
        {"label": "Yarn Count", "fieldname": "yarn_count", "fieldtype": "Data", "width": 100},
        {"label": "Consumption Per LbS", "fieldname": "consumption", "fieldtype": "Float", "width": 140},
        {"label": "Yarn Required", "fieldname": "required", "fieldtype": "Float", "width": 120},
        {"label": "Yarn Received", "fieldname": "received", "fieldtype": "Float", "width": 120},
        {"label": "Yarn Consumed", "fieldname": "consumed", "fieldtype": "Float", "width": 120},
        {"label": "Balance Yarn", "fieldname": "balance_yarn", "fieldtype": "Float", "width": 120},
        {"label": "Balance Fabric", "fieldname": "balance_fabric", "fieldtype": "Float", "width": 120}
    ]
	return columns

def get_conditions(filters):
    conditions = ""
    if filters.get("weaver"):
        conditions += " AND wc.weaver = %(weaver)s"
    if filters.get("construction"):
        conditions += " AND wc.construction = %(construction)s"
    if filters.get("weaving_contract"):
        conditions += " AND wc.name = %(weaving_contract)s"
    if filters.get("date_from"):
        conditions += " AND wc.date >= %(date_from)s"
    if filters.get("date_to"):
        conditions += " AND wc.date <= %(date_to)s"
    return conditions


def get_data(filters):
    conditions = get_conditions(filters)
    data = []

    query = f"""
        SELECT 
            wc.name AS contract_name,
            wc.weaver,
            wc.construction,	
            wc.fabric_qty,
            bom_item.yarn_count,
            bom_item.consumption,
            bom_item.yarn_qty AS required,
            sed.qty AS received,
            bom_item_dn.yarn_qty AS consumed,
            (IFNULL(sed.qty, 0) - IFNULL(dni.qty, 0)) AS balance_yarn,
            (IFNULL(wc.fabric_qty, 0) - IFNULL(dni.qty, 0)) AS balance_fabric
        FROM `tabWeaving Contract` AS wc
        LEFT JOIN `tabBOM Items` AS bom_item ON bom_item.parent = wc.name
        LEFT JOIN `tabStock Entry Detail` AS sed ON sed.weaving_contract = wc.name
        LEFT JOIN `tabDelivery Note Item` AS dni ON dni.custom_weaving_contract = wc.name
        LEFT JOIN `tabBOM Items Dn` AS bom_item_dn ON bom_item_dn.weaving_contract = wc.name
        WHERE 1=1 {conditions}
    """

    data = frappe.db.sql(query, filters, as_dict=True)
    return data