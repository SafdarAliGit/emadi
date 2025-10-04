import frappe

def execute(filters=None):
    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 140},
        {"label": "Quality", "fieldname": "quality", "fieldtype": "Data", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": "Meter", "fieldname": "yarn_qty", "fieldtype": "Float", "width": 120},
        {"label": "Consumption", "fieldname": "consumption", "fieldtype": "Float", "width": 120},
        {"label": "Pick", "fieldname": "pick", "fieldtype": "Data", "width": 100},
    ]

    quality_filters = ""
    if filters.get("quality"):
        qualities = ", ".join([f"'{q}'" for q in filters.get("quality")])
        quality_filters += f" AND fp.fabric_item IN ({qualities})"

    # ── Fetch Data CLOTH ─────────────────────────────
    cloth_data = frappe.db.sql(f"""
        SELECT
            fpi.warehouse,
            fpi.yarn_qty,
            fpi.consumption,
            fp.fabric_item AS quality,
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
        ORDER BY
            fp.posting_date DESC, fpi.name ASC
    	""", filters, as_dict=True)
 	# Totals
        # Totals
    total_meter_cloth = sum((row.get("yarn_qty") or 0) for row in cloth_data)
    total_consumption_cloth = sum((row.get("consumption") or 0) for row in cloth_data)

    # ── Prepare Data ─────────────────────────────
    data = []

    # Header row
    data.append({
        "posting_date": "",
        "quality": "",
        "warehouse": "CLOTH",
        "yarn_qty": "",
        "consumption": "",
        "pick": ""
    })

    # Main data
    data.extend(cloth_data)

   
    data.append({
        "posting_date": "",
        "quality": "",
        "warehouse": "Total",
        "yarn_qty": round(total_meter_cloth, 2),
        "consumption": round(total_consumption_cloth, 2),
        "pick": ""
    })


	# ── Fetch Data YARN ─────────────────────────────
    yarn_data = frappe.db.sql(f"""
        SELECT
            fpi.warehouse,
            fpi.yarn_qty,
            fpi.consumption,
            fp.fabric_item AS quality,
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
        ORDER BY
            fp.posting_date DESC, fpi.name ASC
    	""", filters, as_dict=True)
 	# Totals
        # Totals
    total_meter_yarn = sum((row.get("yarn_qty") or 0) for row in yarn_data)
    total_consumption_yarn = sum((row.get("consumption") or 0) for row in yarn_data)

    # ── Prepare Data ─────────────────────────────

    # Header row
    data.append({
        "posting_date": "",
        "quality": "",
        "warehouse": "YARN",
        "yarn_qty": "",
        "consumption": "",
        "pick": ""
    })

    # Main data
    data.extend(yarn_data)

   
    data.append({
        "posting_date": "",
        "quality": "",
        "warehouse": "Total",
        "yarn_qty": round(total_meter_yarn, 2),
        "consumption": round(total_consumption_yarn, 2),
        "pick": ""
    })

    return columns, data
