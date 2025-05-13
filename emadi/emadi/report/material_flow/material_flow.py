import frappe

def execute(filters=None):
    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Gate Pass", "fieldname": "gate_pass", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Item", "fieldname": "yarn_item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 100},
        {"label": "Bags", "fieldname": "bags", "fieldtype": "Float", "width": 80},
        {"label": "Lbs", "fieldname": "lbs", "fieldtype": "Float", "width": 80},
        {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Count", "fieldname": "yarn_count", "fieldtype": "Data", "width": 100}
    ]

    conditions = ""
    if filters.get("brand"):
        conditions += " AND sed.brand = %(brand)s"
    if filters.get("yarn_count"):
        conditions += " AND item.item_code = %(yarn_count)s"

    data = frappe.db.sql(f"""
        SELECT
            se.posting_date,
            se.manual_sr_no AS gate_pass,
            sed.item_code AS yarn_item,
            sed.brand,
            sed.qty_pcs AS bags,
            sed.qty AS lbs,
            sed.`for` AS purpose,
            sed.item_code AS yarn_count
        FROM
            `tabStock Entry` se
        LEFT JOIN
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE
            se.docstatus = 1 {conditions}
			AND se.stock_entry_type = 'Material Receipt'
        ORDER BY
            se.posting_date DESC
    """, filters, as_dict=True)

    return columns, data
