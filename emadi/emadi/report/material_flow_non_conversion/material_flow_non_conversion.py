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
        {"label": "Lbs", "fieldname": "lbs", "fieldtype": "Data", "width": 120},
        {"label": "Meter", "fieldname": "meter", "fieldtype": "Data", "width": 120},
        {"label": "Return", "fieldname": "return", "fieldtype": "Data", "width": 120}
    ]
    opening_qty_filter = ""
    conditions = ""
    conditions2 = ""
    weft_production_conditions = ""
    sizing_program_conditions = ""
    warp_production_conditions = ""
    delivery_conditions_master = ""
    delivery_conditions = ""

    p = filters.get("p")

    if filters.get("brand"):
        conditions += " AND sed.brand = %(brand)s"
    if filters.get("yarn_count"):
        opening_qty_filter += " AND sri.`item_code` = %(yarn_count)s"
        conditions += " AND sed.`for` = 'Warp' AND sed.item_code = %(yarn_count)s"

    if filters.get("brand"):
        conditions2 += " AND sri.brand = %(brand)s"
    if filters.get("yarn_count_weft"):
        opening_qty_filter += " AND sri.`item_code` = %(yarn_count_weft)s"
        conditions2 += " AND sed.`for` = 'Weft' AND sed.item_code = %(yarn_count_weft)s"
        
    if filters.get("yarn_count_weft"):
        weft_production_conditions += " AND fpi.yarn_count = %(yarn_count_weft)s"
    if filters.get("fabric_item"):
        weft_production_conditions += " AND fp.fabric_item = %(fabric_item)s"

    if filters.get("fabric_item"):
        warp_production_conditions += " AND fp.fabric_item = %(fabric_item)s"

    if filters.get("fabric_item"):
        sizing_program_conditions += " AND sp.fabric_construction = %(fabric_item)s"
    
    if filters.get("fabric_item"):
        delivery_conditions += " AND dn.fabric_item = %(fabric_item)s"
    if filters.get("brand"):
        delivery_conditions += " AND bid.brand = %(brand)s"

    # if filters.get("customer"):
    #     delivery_conditions_master += " AND dn.customer = %(customer)s"
    if filters.get("fabric_item"):
        delivery_conditions_master += " AND sii.item_code = %(fabric_item)s"

    
    data = []

    # opening qty
    opening_qty = frappe.db.sql(f"""
    SELECT 
        sri.item_code as yarn_item,
        SUM(CASE WHEN sri.item_group = 'Yarn' THEN sri.qty ELSE 0 END) as lbs,
        SUM(CASE WHEN sri.item_group = 'Beam' THEN sri.qty ELSE 0 END) as meter
    FROM `tabStock Reconciliation Item` sri
    LEFT JOIN `tabStock Reconciliation` sr ON sri.parent = sr.name
    WHERE
        sr.docstatus = 1
    GROUP BY sri.item_code
    """, filters, as_dict=True)

    if opening_qty:
        data.append({
            "posting_date": "<b>Opening Qty</b>",
            "gate_pass": "",
            "yarn_item": "",
            "brand": "",
            "bags": "",
            "lbs": "",
            "meter": "",
            "purpose": "",
            "yarn_count": "",
            "return": ""
        })
        data.extend(opening_qty)
    # Warp Data
    data_warp = frappe.db.sql(f"""
    SELECT
        se.posting_date,
        se.manual_sr_no AS gate_pass,
        sed.item_code AS yarn_item,
        sed.brand,
        sed.qty_pcs AS bags,
        ROUND(CASE WHEN se.stock_entry_type = 'Material Receipt' AND sed.uom = 'Lbs' THEN sed.qty ELSE 0 END, 5) AS lbs,
        ROUND(CASE WHEN se.stock_entry_type = 'Material Receipt' AND sed.uom = 'Meter' THEN sed.qty ELSE 0 END, 5) AS meter,
        sed.`for` AS purpose,
        sed.item_code AS yarn_count,
        ROUND(CASE WHEN se.stock_entry_type = 'Material Issue' THEN sed.qty ELSE 0 END, 5) AS `return`
    FROM
        `tabStock Entry` se
    LEFT JOIN
        `tabStock Entry Detail` sed ON se.name = sed.parent
    WHERE
        se.docstatus = 1 
        {conditions}
    ORDER BY
        se.posting_date DESC
    """, filters, as_dict=True)
    
    # Calculate total lbs for warp
    total_received = sum(row["lbs"] or 0 for row in data_warp)
    total_received_meter_warp = sum(row["meter"] or 0 for row in data_warp)
    total_return = sum(row["return"] or 0 for row in data_warp)
    total_received_warp = sum(row["lbs"] or 0 for row in data_warp if row["purpose"] == "Warp")

    # Add total row for warp
    if data_warp:
        data_warp.append({
        "posting_date": "<b>Total Warp Received</b>",
        "gate_pass": "Warp: " + "<b>" + str(round(total_received_warp, 2)) + "</b>",
        "yarn_item": "",
        "brand": "",
        "bags": "",
        "lbs": "<b>" + str(round(total_received, 2)) + "</b>",
        "meter": "<b>" + str(round(total_received_meter_warp, 2)) + " Mtr</b>",
        "purpose": "",
        "yarn_count": "",
        "return": "<b>" + str(round(total_return, 2)) + "</b>"
    })

    # Weft Data
    data_weft = frappe.db.sql(f"""
        SELECT
            se.posting_date,
            se.manual_sr_no AS gate_pass,
            sed.item_code AS yarn_item,
            sed.brand,
            sed.qty_pcs AS bags,
            ROUND(CASE WHEN se.stock_entry_type = 'Material Receipt' AND sed.uom = 'Lbs' THEN sed.qty ELSE 0 END, 5) AS lbs,
            ROUND(CASE WHEN se.stock_entry_type = 'Material Receipt' AND sed.uom = 'Meter' THEN sed.qty ELSE 0 END, 5) AS meter,
            sed.`for` AS purpose,
            sed.item_code AS yarn_count,
            ROUND(CASE WHEN se.stock_entry_type = 'Material Issue' THEN sed.qty ELSE 0 END, 5) AS `return`
        FROM
            `tabStock Entry` se
        LEFT JOIN
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE
            se.docstatus = 1 
            {conditions2}
        ORDER BY
            se.posting_date DESC
    """, filters, as_dict=True)

    # Calculate total lbs for weft
    total_received = sum(row["lbs"] or 0 for row in data_weft)
    total_received_meter = sum(row["meter"] or 0 for row in data_weft)
    total_return = sum(row["return"] or 0 for row in data_weft)
    total_received_weft = sum(row["lbs"] or 0 for row in data_weft if row["purpose"] == "Weft")
    total_received_weft_meter = sum(row["meter"] or 0 for row in data_weft if row["purpose"] == "Weft")

    # Add total row for weft
    if data_weft:
        data_weft.append({
            "posting_date": "<b>Total Weft Received</b>",
            "gate_pass": "",
            "yarn_item": "Weft: " + str(round(total_received_weft, 2)),
            "brand": "",
            "bags": "",
            "lbs": "<b>" + str(round(total_received, 2)) + "</b>",
            "meter": "<b>" + str(round(total_received_meter, 2)) + " Mtr</b>",
            "purpose": "",
            "yarn_count": "",
            "return": "<b>" + str(round(total_return, 2)) + "</b>"
        })
        data_weft.append({
            "posting_date": "<b style='font-size: 14px;'>WEFT Detail</b>",
            "gate_pass": "<b style='font-size: 12px;'>(Fabric Production)</b>",
            "yarn_item": "",
            "brand": "",
            "bags": "",
            "lbs": "",
            "purpose": "",
            "yarn_count": ""
        })
    data.extend(data_warp)
    data.extend(data_weft)

    # Weft Production Data
    weft_production_data = frappe.db.sql(f"""
        SELECT
            fp.posting_date,
            fp.name as gate_pass,
            fp.quality as yarn_count,
            fpi.yarn_count as yarn_item,
            ROUND(fpi.yarn_qty, 5) AS lbs,
            ROUND(fpi.beam_length, 5) AS meter
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
    total_weft_meter = sum(row["meter"] or 0 for row in weft_production_data)
    if weft_production_data:
        weft_production_data.append({
            "posting_date": "<b>Total Weft</b>",
            "yarn_item": "",
            "purpose": "",
            "lbs": "<b>" + str(round(total_weft, 2)) + "</b>",
            "gate_pass": ""
        })

    data.extend(weft_production_data)

    # Warp Consumption (Sizing Program)
    data.append({
        "posting_date": "<b style='font-size: 14px;'>Warp Consumption</b>",
        "gate_pass": "<b style='font-size: 12px;'>(Sizing Program)</b>",
        "yarn_item": "",
        "brand": "",
        "bags": "",
        "lbs": "",
        "meter": "",
        "purpose": "",
        "yarn_count": ""
    })

    sizing_program_data = frappe.db.sql(f"""
        SELECT
            sp.name AS gate_pass,
            '' as bags,
            ROUND(spi.lbs, 5) AS lbs,
            ROUND(spi.length, 5) AS meter
        FROM
            `tabSizing Program` AS sp
        LEFT JOIN
            `tabSizing Program Item` AS spi ON sp.name = spi.parent
        WHERE
            sp.docstatus = 1
            {sizing_program_conditions}
    """, filters, as_dict=True)

    total_warp = sum(row["lbs"] or 0 for row in sizing_program_data)
    total_production_length = sum(row["meter"] or 0 for row in sizing_program_data)
    ratio = total_warp / total_production_length if total_production_length else 0

    if sizing_program_data:
        sizing_program_data.append({
            "posting_date": "<b>Total Warp</b>",
            "yarn_item": "",
            "purpose": "Ratio: " + str(round(ratio, 4)) if ratio else "Ratio: 0",
            "bags": "",
            "lbs": "<b>" + str(round(total_warp, 2)) + "</b>",
            "meter":"<b>" + str(round(total_production_length, 2)) + " Mtr</b>",
            "gate_pass": ""
        })

    data.extend(sizing_program_data)

    # WARP Detail (Fabric Production)
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
            ROUND(fpi.yarn_qty, 5) AS meter
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

    total_warp = sum(row["meter"] or 0 for row in warp_production_data)
    if warp_production_data:
        warp_production_data.append({
            "posting_date": "<b>Total Warp</b>",
            "yarn_item": "",
            "purpose": "",
            "bags": "",
            "lbs": "LBS : " + "<b>" + str(round(total_warp * (ratio if ratio else 1), 2)) + "</b>",
            "meter":"<b>" + str(round(total_warp, 2)) + " Mtr</b>",
            "gate_pass": ""
        })

    data.extend(warp_production_data)

    # Yarn Balance Calculation
    waste_percentage_bags = float(total_production_length if total_production_length else total_received_meter_warp if total_received_meter_warp else 0) * (float(p) / 100) if p else 0
    remaining_bags = (total_production_length if total_production_length else total_received_meter_warp if total_received_meter_warp else 0) - waste_percentage_bags
    yarn_balance_data = [{
        "posting_date": "<b>Yarn Warp Balance(Length)</b>",
        "gate_pass": "",
        "yarn_item": "Waste %: " + str(p) + "%",
        "brand": "Waste: " + str(round(waste_percentage_bags, 2)),
        "bags": "",
        "lbs": str(round(((remaining_bags if remaining_bags else 0) - (total_warp if total_warp else 0)) * (ratio if ratio else 1), 2)),
        "meter":str(round(remaining_bags - total_warp if total_warp else 0, 2)) + " Mtr",
        "purpose": "Remaining: " + str(round(remaining_bags, 2)),
        "yarn_count": ""
    }]

    data.extend(yarn_balance_data)

    # Delivery Detail
    delivery_fabric_qty = frappe.db.sql(f"""
        SELECT
            SUM(sii.qty) AS yarn_item
        FROM
            `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            {delivery_conditions_master}
            AND si.is_return = 0
    """, filters, as_dict=True)


    delivery_fabric_qty_with_return = frappe.db.sql(f"""
        SELECT
            SUM(sii.qty) AS yarn_item
        FROM
            `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            {delivery_conditions_master}
    """, filters, as_dict=True)

    data.append({
        "posting_date": "<b style='font-size: 14px;'>Delivery Detail (Fabric)</b>",
        "gate_pass": "",
        "yarn_item": "",
        "brand": "",
        "bags": "",
        "lbs": "",
        "purpose": "",
        "yarn_count": ""
    })

    data.append({
        "posting_date": "<b>Fabric Qty (With Return)</b>",
        "gate_pass": "",
        "yarn_item": "",
        "brand": "",
        "bags": "",
        "lbs": "",
        "meter":str(round(delivery_fabric_qty[0].yarn_item if delivery_fabric_qty and delivery_fabric_qty[0].yarn_item else 0, 2)) + " Mtr",
        "purpose": "",
        "yarn_count": ""
    })

    data.append({
        "posting_date": "<b>Fabric Qty (Without Return)</b>",
        "gate_pass": "",
        "yarn_item": "",
        "brand": "",
        "bags": "",
        "lbs": "",
        "meter":str(round(delivery_fabric_qty_with_return[0].yarn_item if delivery_fabric_qty_with_return and delivery_fabric_qty_with_return[0].yarn_item else 0, 2)) + " Mtr",
        "purpose": "",
        "yarn_count": ""
    })

    data.append({
        "posting_date": "<b>Fabric Balance</b>",
        "gate_pass": "",
        "yarn_item": "",
        "brand": "",
        "bags": "",
        "lbs": "",
        "meter":str(round((total_production_length if total_production_length else 0) - (delivery_fabric_qty_with_return[0].yarn_item if delivery_fabric_qty_with_return and delivery_fabric_qty_with_return[0].yarn_item else 0), 2)) + " Mtr",
        "purpose": "",
        "yarn_count": ""
    })

    data.append({
        "posting_date": "<b>Shortage/Gain</b>",
        "gate_pass": "",
        "yarn_item": "",
        "brand": "",
        "bags": str(round((remaining_bags if remaining_bags else 0) - (delivery_fabric_qty_with_return[0].yarn_item if delivery_fabric_qty_with_return and delivery_fabric_qty_with_return[0].yarn_item else 0), 2)),
        "lbs": "",
        "meter":str(round(((remaining_bags if remaining_bags else 0) - (delivery_fabric_qty_with_return[0].yarn_item if delivery_fabric_qty_with_return and delivery_fabric_qty_with_return[0].yarn_item else 0)) * (ratio or 0), 2)) + " Mtr",
        "purpose": "",
        "yarn_count": ""
    })

    data.append({
        "posting_date": "<b>Shortage/Gain %</b>",
        "gate_pass": "",
        "yarn_item": "",
        "brand": "",
        "bags": str(round(((round(total_production_length if total_production_length else total_received_meter_warp if total_received_meter_warp else 0, 2) - round(delivery_fabric_qty_with_return[0].yarn_item if delivery_fabric_qty_with_return and delivery_fabric_qty_with_return[0].yarn_item else 0, 2)) / (total_production_length if total_production_length else total_received_meter_warp if total_received_meter_warp else 1) * 100), 2)),
        "lbs": "",
        "purpose": "",
        "yarn_count": ""
    })

    # Warp Weft Detail
    data.append({
        "posting_date": "",
        "gate_pass": "Fabric Item",
        "yarn_item": "",
        "brand": "",
        "bags": "Warp Qty",
        "lbs": "Weft Qty",
        "purpose": "",
        "yarn_count": ""
    })

    delivery_data = frappe.db.sql(f"""
        SELECT
            "" as posting_date,
            "" as gate_pass,
            dn.fabric_item as gate_pass,
            "" as yarn_item,
            SUM(CASE WHEN bid.for = 'Warp' THEN bid.yarn_qty ELSE 0 END) as bags,
            SUM(CASE WHEN bid.for = 'Weft' THEN bid.yarn_qty ELSE 0 END) as lbs
        FROM
            `tabDelivery Note` dn
        LEFT JOIN
            `tabBOM Items Dn` bid ON dn.name = bid.parent
        WHERE
            dn.docstatus = 1 {delivery_conditions}
        GROUP BY
            dn.fabric_item
    """, filters, as_dict=True)

    total_warp = sum(row["bags"] or 0 for row in delivery_data)
    total_weft = sum(row["lbs"] or 0 for row in delivery_data)
    if delivery_data:
        # delivery_data.append({
        #         "posting_date": "<b>Warp + Weft(Customer Ratio)</b>",
        #         "yarn_item": "",
        #         "purpose": "",
        #         "brand": "",
        #         "bags": "",
        #         "lbs": "<b>" + str(round((total_warp) + (total_weft), 2)) + "</b>",
        #         "gate_pass": ""
        #     })
    
        delivery_data.append({
            "posting_date": "<b>Yarn Balance(Customer)</b>",
            "yarn_item": "",
            "purpose": "",
            "brand": "",
            "bags": "<b>" + str(round(total_received_warp - total_warp, 2) if total_received_warp > 0 else 0) + "</b>",
            "lbs": "<b>" + str(round(total_received_weft - total_weft, 2)) + "</b>",
            "meter": "<b>" + str(
        round(
            total_received_meter_warp - round(
                delivery_fabric_qty[0].yarn_item if (delivery_fabric_qty and delivery_fabric_qty[0].yarn_item) else 0,
                2
            ),
            2
        ) if total_received_meter_warp > 0 else 0
    ) + " Mtr</b>",
    "gate_pass": ""
        })
        

    data.extend(delivery_data)
    return columns, data





