import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {"label": "Transaction #", "fieldname": "stock_entry_name", "fieldtype": "Data", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Fabric Item", "fieldname": "fabric_item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label":"Consumption", "fieldname": "consumption", "fieldtype": "Float", "width": 120},
        {"label": "For", "fieldname": "about", "fieldtype": "Data", "width": 120},
        {"label": "Target Warehouse", "fieldname": "t_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 180},
        {"label": "Fabric Qty", "fieldname": "fabric_qty", "fieldtype": "Float", "width": 120},
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 120},
        
    ]
    return columns


def get_conditions_se(filters, doctype):
    conditions = []

    if filters.get("from_date"):
        conditions.append(f"`{doctype}`.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"`{doctype}`.posting_date <= %(to_date)s")
    if filters.get("brand"):
        conditions.append(f"`sed`.brand = %(brand)s")
    return " AND ".join(conditions) if conditions else "1=1"

def get_conditions_dn(filters, doctype):
    conditions = []

    if filters.get("from_date"):
        conditions.append(f"`{doctype}`.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"`{doctype}`.posting_date <= %(to_date)s")
    if filters.get("brand"):
        conditions.append(f"`dni`.brand = %(brand)s")
    return " AND ".join(conditions) if conditions else "1=1"


def get_data(filters):
    data = []
    weaving_stock = """SELECT 
            se.posting_date,
            se.name AS stock_entry_name,
            sed.item_code,
            sed.qty,
            sed.for AS about,
            sed.t_warehouse,
            '' AS fabric_item,
            '' AS fabric_qty,
            '' AS consumption

        FROM 
            `tabStock Entry` se
        LEFT JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE 
            se.docstatus = 1
            AND
            se.stock_entry_type = 'Material Receipt'
            AND
            {conditions}
    """.format(conditions=get_conditions_se(filters, "se"))
    
    weaving_stock_result = frappe.db.sql(weaving_stock, filters, as_dict=1)

    total_qty = 0
    for i in weaving_stock_result:
        total_qty += i.get('qty',0)

    weaving_stock_heading = [{"posting_date": "", "stock_entry_name": "<span style='font-size: 14px;font-weight: bold;'>Stock Entry</span>", "item_code": "", "qty": "", "about": "", "t_warehouse": "", "fabric_item": "", "fabric_qty": "", "consumption": ""}]
    weaving_stock_result = weaving_stock_heading + weaving_stock_result
    weaving_stock_total = [{"posting_date": "", "stock_entry_name": "<span style='font-weight: bold;'>Total Qty</span>", "item_code": "", "qty": total_qty, "about": "", "t_warehouse": "", "fabric_item": "", "fabric_qty": "", "consumption": ""}]

    weaving_stock_result.extend(weaving_stock_total)
    

    dn_stock = """SELECT 
            dn.posting_date,
            dn.name AS stock_entry_name,
            dn.fabric_item,
            dn.fabric_qty,
            dni.yarn_count AS item_code,
            dni.consumption,
            dni.yarn_qty AS qty,
            dni.for AS about,
            '' AS t_warehouse
            

        FROM 
            `tabDelivery Note` dn
        LEFT JOIN 
            `tabBOM Items Dn` dni ON dn.name = dni.parent
        WHERE 
            dn.docstatus = 1
            AND
            {conditions}
    """.format(conditions=get_conditions_dn(filters, "dn"))

    dn_stock_result = frappe.db.sql(dn_stock, filters, as_dict=1)
    total_qty = 0
    for i in dn_stock_result:
        total_qty += i.get('qty',0)

    dn_stock_heading = [{"posting_date": "", "stock_entry_name": "<span style='font-size: 14px;font-weight: bold;'>Delivery Note</span>", "item_code": "", "qty": "", "about": "", "t_warehouse": "", "fabric_item": "", "fabric_qty": "", "consumption": ""}]
    dn_stock_result = dn_stock_heading + dn_stock_result
    dn_stock_total = [{"posting_date": "", "stock_entry_name": "<span style='font-weight: bold;'>Total Qty</span>", "item_code": "", "qty": total_qty, "about": "", "t_warehouse": "", "fabric_item": "", "fabric_qty": '', "consumption": ""}]
    dn_stock_result.extend(dn_stock_total)



    data.extend(weaving_stock_result)
    data.extend(dn_stock_result)
    return data


