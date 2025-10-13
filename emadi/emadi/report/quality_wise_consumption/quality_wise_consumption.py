import frappe

def execute(filters=None):
    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 140},
        {"label": "Quality", "fieldname": "quality", "fieldtype": "Data", "width": 120},
        {"label": "Yarn Count", "fieldname": "yarn_count", "fieldtype": "Data", "width": 120},
         {"label": "Meter", "fieldname": "yarn_qty", "fieldtype": "Float", "width": 120},
        {"label": "Lbs", "fieldname": "yarn", "fieldtype": "Float", "width": 120},
        {"label": "Pick", "fieldname": "pick", "fieldtype": "Data", "width": 100},
    ]
     # Return empty data if no filters are applied
    if not filters or not filters.get("fabric_item"):
        return columns, []

    quality_filters = ""
    if filters.get("fabric_item"):
        qualities = ", ".join([f"'{q}'" for q in filters.get("fabric_item")])
        quality_filters += f" AND fp.fabric_item IN ({qualities})"

    # ── Fetch Data CLOTH ─────────────────────────────
    cloth_data = frappe.db.sql(f"""
        SELECT
            SUM(fpi.yarn_qty) as yarn_qty,
            fp.fabric_item AS quality,
            fpi.yarn_count,
            fp.posting_date,
            i.custom_pick AS pick
        FROM
            `tabFabric Production Item` fpi
        INNER JOIN
            `tabFabric Production` fp
            ON fpi.parent = fp.name
        LEFT JOIN
            `tabItem` i
            ON i.name = fp.fabric_item
        WHERE
            fp.docstatus = 1
            AND fpi.`for` = 'Warp'
            {quality_filters}
        GROUP BY
            fp.fabric_item
        ORDER BY
            fp.posting_date DESC, fpi.name ASC
    	""", filters, as_dict=True)
 	
    # Totals
    total_yarn_qty_cloth = sum((row.get("yarn_qty") or 0) for row in cloth_data)

    # ── Prepare Data ─────────────────────────────
    data = []

    # Header row
    data.append({
        "posting_date": "",
        "quality": "CLOTH",
        "yarn_count": "",
        "yarn_qty": "",
        "pick": ""
    })

    # Main data
    data.extend(cloth_data)

    data.append({
        "posting_date": "",
        "quality": "Total",
        "yarn_count": "",
        "yarn_qty": round(total_yarn_qty_cloth, 2),
        "pick": ""
    })


    # ── Fetch Data YARN ─────────────────────────────
    yarn_data = frappe.db.sql(f"""
        SELECT
            SUM(fpi.yarn_qty) as yarn,
            fp.fabric_item AS quality,
            fpi.yarn_count,
            fp.posting_date,
            i.custom_pick AS pick
        FROM
            `tabFabric Production Item` fpi
        INNER JOIN
            `tabFabric Production` fp
            ON fpi.parent = fp.name
        LEFT JOIN
            `tabItem` i
            ON i.name = fp.fabric_item
        WHERE
            fp.docstatus = 1
            AND fpi.`for` = 'Weft'
            {quality_filters}
        GROUP BY
            fpi.yarn_count
        ORDER BY
            fp.posting_date DESC, fpi.name ASC
          
    	""", filters, as_dict=True)
 	
    # # Totals
    total_meter_yarn = sum((row.get("yarn") or 0) for row in yarn_data)

    # ── Prepare Data ─────────────────────────────

    #Header row
    data.append({
        "posting_date": "",
        "quality": "YARN",
        "yarn_count": "",
        "yarn_qty": "",
        "pick": ""
    })

    # Main data
    data.extend(yarn_data)

    data.append({
        "posting_date": "",
        "quality": "Total",
        "yarn_count": "",
        "yarn_qty": round(total_meter_yarn, 2),
        "pick": ""
    })

    return columns, data