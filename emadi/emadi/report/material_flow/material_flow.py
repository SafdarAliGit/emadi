import frappe

def execute(filters=None):
    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": 140},
        {"label": "Gate Pass", "fieldname": "gate_pass", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Item", "fieldname": "yarn_item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 100},
        {"label": "Bags", "fieldname": "bags", "fieldtype": "Data", "width": 80},
        {"label": "Lbs", "fieldname": "lbs", "fieldtype": "Data", "width": 120},
        {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Count", "fieldname": "yarn_count", "fieldtype": "Data", "width": 100}
    ]

    conditions = ""
    if filters.get("brand"):
        conditions += " AND sed.brand = %(brand)s"
    if filters.get("yarn_count"):
        conditions += " AND sed.item_code = %(yarn_count)s"
    
    production_conditions = ""
    if filters.get("yarn_count"):
        production_conditions += " AND fpi.yarn_count = %(yarn_count)s"
    if filters.get("fabric_item"):
        production_conditions += " AND fp.fabric_item = %(fabric_item)s"

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
    # Calculate total lbs
    total_lbs = sum(row["lbs"] or 0 for row in data)

    # Add total row
    if data:
        data.append({
            "posting_date": "<b>Total</b>",  # You can leave empty or write "Total"
            "gate_pass": "",
            "yarn_item": "",
            "brand": "",
            "bags": "",  # Optional: sum bags if needed
            "lbs": total_lbs,
            "purpose": "",
            "yarn_count": ""
        })
        data.append({
            "posting_date": "<b style='font-size: 14px;'>WEFT Detail</b>",
            "gate_pass": "",
            "yarn_item": "",
            "brand": "",
            "bags": "",
            "lbs": "",
            "purpose": "",
            "yarn_count": ""
        })
    production_data = frappe.db.sql(f"""
        SELECT
            "" as posting_date,
            fpi.yarn_count as yarn_item,
            fpi.for as purpose,
            fpi.yarn_qty AS lbs
        FROM
            `tabFabric Production` fp
        LEFT JOIN
            `tabFabric Production Item` fpi ON fp.name = fpi.parent
        WHERE
            fp.docstatus = 1 {production_conditions}
			AND fpi.for = 'Weft'
        ORDER BY
            fp.posting_date DESC
    """, filters, as_dict=True)
    total_production_lbs = sum(row["lbs"] or 0 for row in production_data)
    if production_data:
        production_data.append({
            "posting_date": "<b>Total</b>",
            "yarn_item": "",
            "purpose": "",
            "lbs": total_production_lbs
        })
    data.extend(production_data)
    return columns, data
