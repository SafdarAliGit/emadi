import frappe

def execute(filters=None):
    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": 140},
        {"label": "Gate Pass", "fieldname": "gate_pass", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Item", "fieldname": "yarn_item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 100},
         {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Count", "fieldname": "yarn_count", "fieldtype": "Data", "width": 100},
        {"label": "Bags/Length", "fieldname": "bags", "fieldtype": "Data", "width": 80},
        {"label": "Lbs", "fieldname": "lbs", "fieldtype": "Data", "width": 120}
       
    ]

    conditions = ""
    weft_production_conditions = ""
    sizing_program_conditions = ""
    warp_production_conditions = ""
    p = filters.get("p")

    if filters.get("brand"):
        conditions += " AND sed.brand = %(brand)s"
    if filters.get("yarn_count"):
        conditions += " AND sed.item_code = %(yarn_count)s"
    
    
    if filters.get("yarn_count"):
        weft_production_conditions += " AND fpi.yarn_count = %(yarn_count)s"
    if filters.get("fabric_item"):
        weft_production_conditions += " AND fp.fabric_item = %(fabric_item)s"

    if filters.get("fabric_item"):
        warp_production_conditions += " AND fp.fabric_item = %(fabric_item)s"

    if filters.get("fabric_item"):
        sizing_program_conditions += " AND sp.fabric_construction = %(fabric_item)s"
    
    data = frappe.db.sql(f"""
        SELECT
            se.posting_date,
            se.manual_sr_no AS gate_pass,
            sed.item_code AS yarn_item,
            sed.brand,
            sed.qty_pcs AS bags,
            ROUND(sed.qty, 5) AS lbs,
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
    total_received = sum(row["lbs"] or 0 for row in data)
    total_received_warp = sum(row["lbs"] or 0 for row in data if row["purpose"] == "Warp")
    total_received_weft = sum(row["lbs"] or 0 for row in data if row["purpose"] == "Weft")

    # Add total row
    if data:
        data.append({
            "posting_date": "<b>Total Received</b>",  # You can leave empty or write "Total"
            "gate_pass": "Warp: " + str(round(total_received_warp,2)),
            "yarn_item": "Weft: " + str(round(total_received_weft,2)),
            "brand": "",
            "bags": "",  # Optional: sum bags if needed
            "lbs": round(total_received,2),
            "purpose": "",
            "yarn_count": ""
        })
        data.append({
            "posting_date": "<b style='font-size: 14px;'>WEFT Detail</b>",
            "gate_pass": "<b style='font-size: 12px;'>(Fabric Production)</b>",
            "yarn_item": "",
            "brand": "",
            "bags": "",
            "lbs": "",
            "purpose": "",
            "yarn_count": ""
        })
    weft_production_data = frappe.db.sql(f"""
        SELECT
            fp.posting_date,
            fp.name as gate_pass,
            fp.quality as yarn_count,
            fpi.yarn_count as yarn_item,
            ROUND(fpi.yarn_qty, 5) AS lbs
        FROM
            `tabFabric Production` fp
        LEFT JOIN
            `tabFabric Production Item` fpi ON fp.name = fpi.parent
        WHERE
            fp.docstatus = 1 {weft_production_conditions}
			AND fpi.for = 'Weft'
        ORDER BY
            fp.posting_date DESC
    """, filters, as_dict=True)
    total_weft = sum(row["lbs"] or 0 for row in weft_production_data)
    if weft_production_data:
        weft_production_data.append({
            "posting_date": "<b>Total Weft</b>",
            "yarn_item": "",
            "purpose": "",
            "lbs": round(total_weft,2),
            "gate_pass": ""
        })
    data.extend(weft_production_data)
    data.append({
            "posting_date": "<b style='font-size: 14px;'>Warp Consumption</b>",
            "gate_pass": "<b style='font-size: 12px;'>(Sizing Program)</b>",
            "yarn_item": "",
            "brand": "",
            "bags": "",
            "lbs": "",
            "purpose": "",
            "yarn_count": ""
        })
    sizing_program_data = frappe.db.sql(f"""
        SELECT
            sp.name AS gate_pass,
            spi.length as bags,
            ROUND(spi.lbs, 5) AS lbs
        FROM
            `tabSizing Program` AS sp
        LEFT JOIN
            `tabSizing Program Item` AS spi ON sp.name = spi.parent
        WHERE
            sp.docstatus = 1
            {sizing_program_conditions}
    """, filters, as_dict=True)
    total_warp = sum(row["lbs"] or 0 for row in sizing_program_data)
    total_production_length = sum(row["bags"] or 0 for row in sizing_program_data)
    ratio = total_warp / total_production_length
    if sizing_program_data:
        sizing_program_data.append({
            "posting_date": "<b>Total Warp</b>",
            "yarn_item": "",
            "purpose": "Ratio: " + str(ratio),
            "bags": round(total_production_length,2),
            "lbs": round(total_warp,2),
            "gate_pass": ""
        })
    data.extend(sizing_program_data)

    data.append({
            "posting_date": "<b style='font-size: 14px;'>WARP Detail</b>",
            "gate_pass": "<b style='font-size: 12px;'>(Fabric Production)</b>",
            "yarn_item": "",
            "brand": "",
            "bags": "",
            "lbs": "",
            "purpose": "",
            "yarn_count": ""
        })

    warp_production_data = frappe.db.sql(f"""
        SELECT
            fp.posting_date,
            fp.name as gate_pass,
            fp.quality as yarn_count,
            fpi.yarn_count as yarn_item,
            ROUND(fpi.yarn_qty, 5) AS bags
        FROM
            `tabFabric Production` fp
        LEFT JOIN
            `tabFabric Production Item` fpi ON fp.name = fpi.parent
        WHERE
            fp.docstatus = 1 {warp_production_conditions}
			AND fpi.for = 'Warp'
        ORDER BY
            fp.posting_date DESC
    """, filters, as_dict=True)
    total_warp = sum(row["bags"] or 0 for row in warp_production_data)
    if warp_production_data:
        warp_production_data.append({
            "posting_date": "<b>Total Warp</b>",
            "yarn_item": "",
            "purpose": "",
            "bags":round(total_warp,2),
            "lbs":"LBS : " + str(round(total_warp *(ratio if ratio else 1),2)),
            "gate_pass": ""
        })
    data.extend(warp_production_data)


    # yarn_balance = total_received - (total_weft + total_warp)

    waste_percentage_bags = float(total_production_length) * (float(p) / 100)
    remaining_bags = total_production_length - waste_percentage_bags
    yarn_balance_data = [{"posting_date": "<b>Yarn Warp Balance(Length)</b>", "gate_pass": "", "yarn_item": "Waste %: " + str(p) + "%", "brand": "Waste: " + str(round(waste_percentage_bags,2)), "bags":str(round(remaining_bags,2)-total_warp if total_warp else 0) , "lbs":"", "purpose": "Remaining: " + str(round(remaining_bags,2)), "yarn_count": ""}]
    data.extend(yarn_balance_data)
    
    return columns, data



