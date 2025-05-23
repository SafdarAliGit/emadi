import frappe
from collections import defaultdict

def execute(filters=None):
    if not filters:
        filters = {}

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if not start_date or not end_date:
        frappe.throw("Please select Start Date and End Date")

    data = get_merged_looms_data(start_date, end_date)
    columns = get_columns()

    return columns, data

def get_columns():
    columns = [
        {"label": "Parent", "fieldname": "parent", "fieldtype": "Data", "width": 150},

        # Shift A columns
        {"label": "Shift A Loom", "fieldname": "a_loom", "fieldtype": "Data", "width": 120},
        {"label": "Shift A Sizing Name", "fieldname": "a_sizing_name", "fieldtype": "Data", "width": 140},
        {"label": "Shift A RPM", "fieldname": "a_rpm", "fieldtype": "Data", "width": 80},
        {"label": "Shift A Unit per RPM", "fieldname": "a_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Shift A Efficiency", "fieldname": "a_effeciency", "fieldtype": "Data", "width": 100},

        # Shift B columns
        {"label": "Shift B Loom", "fieldname": "b_loom", "fieldtype": "Data", "width": 120},
        {"label": "Shift B Sizing Name", "fieldname": "b_sizing_name", "fieldtype": "Data", "width": 140},
        {"label": "Shift B RPM", "fieldname": "b_rpm", "fieldtype": "Data", "width": 80},
        {"label": "Shift B Unit per RPM", "fieldname": "b_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Shift B Efficiency", "fieldname": "b_effeciency", "fieldtype": "Data", "width": 100},

        # Shift C columns
        {"label": "Shift C Loom", "fieldname": "c_loom", "fieldtype": "Data", "width": 120},
        {"label": "Shift C Sizing Name", "fieldname": "c_sizing_name", "fieldtype": "Data", "width": 140},
        {"label": "Shift C RPM", "fieldname": "c_rpm", "fieldtype": "Data", "width": 80},
        {"label": "Shift C Unit per RPM", "fieldname": "c_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Shift C Efficiency", "fieldname": "c_effeciency", "fieldtype": "Data", "width": 100},
    ]
    return columns

def get_merged_looms_data(start_date, end_date):
    shift_a = frappe.db.sql("""
        SELECT d.parent, d.loom, d.sizing_name, d.rpm, d.unit_per_rpm, d.effeciency
        FROM `tabLoom Production Items` d
        JOIN `tabLoom Production` m ON d.parent = m.name
        WHERE m.shift = 'Shift-A'
          AND m.date >= %(start_date)s AND m.date <= %(end_date)s
        ORDER BY d.loom
    """, {"start_date": start_date, "end_date": end_date}, as_dict=True)

    shift_b = frappe.db.sql("""
        SELECT d.parent, d.loom, d.sizing_name, d.rpm, d.unit_per_rpm, d.effeciency
        FROM `tabLoom Production Items` d
        JOIN `tabLoom Production` m ON d.parent = m.name
        WHERE m.shift = 'Shift-B'
          AND m.date >= %(start_date)s AND m.date <= %(end_date)s
        ORDER BY d.loom
    """, {"start_date": start_date, "end_date": end_date}, as_dict=True)

    shift_c = frappe.db.sql("""
        SELECT d.parent, d.loom, d.sizing_name, d.rpm, d.unit_per_rpm, d.effeciency
        FROM `tabLoom Production Items` d
        JOIN `tabLoom Production` m ON d.parent = m.name
        WHERE m.shift = 'Shift-C'
          AND m.date >= %(start_date)s AND m.date <= %(end_date)s
        ORDER BY d.loom
    """, {"start_date": start_date, "end_date": end_date}, as_dict=True)

    max_len = max(len(shift_a), len(shift_b), len(shift_c))

    merged_rows = []

    # Add the header row
    merged_rows.append({
        'parent': '',

        'a_loom': '<b style="color: green;text-align: center;">----</b>',
        'a_sizing_name': '<b style="color: green;text-align: center;">----</b>',
        'a_rpm': '<b style="color: green;text-align: center;">Shift - A</b>',
        'a_unit_per_rpm': '<b style="color: green;text-align: center;">----</b>',
        'a_effeciency': '<b style="color: green;text-align: center;">----</b>',

        'b_loom': '<b style="color: orange;text-align: center;">----</b>',
        'b_sizing_name': '<b style="color: orange;text-align: center;">----</b>',
        'b_rpm': '<b style="color: orange;text-align: center;">Shift - B</b>',
        'b_unit_per_rpm': '<b style="color: orange;text-align: center;">----</b>',
        'b_effeciency': '<b style="color: orange;text-align: center;">----</b>',

        'c_loom': '<b style="color: blue;text-align: center;">----</b>',
        'c_sizing_name': '<b style="color: blue;text-align: center;">----</b>',
        'c_rpm': '<b style="color: blue;text-align: center;">Shift - C</b>',
        'c_unit_per_rpm': '<b style="color: blue;text-align: center;">----</b>',
        'c_effeciency': '<b style="color: blue;text-align: center;">----</b>',
    })

    # Add actual data rows
    for i in range(max_len):
        row = {
            'parent': (shift_a[i]['parent'] if i < len(shift_a) else
                       shift_b[i]['parent'] if i < len(shift_b) else
                       shift_c[i]['parent'] if i < len(shift_c) else None),

            'a_loom': shift_a[i]['loom'] if i < len(shift_a) else None,
            'a_sizing_name': shift_a[i]['sizing_name'] if i < len(shift_a) else None,
            'a_rpm': shift_a[i]['rpm'] if i < len(shift_a) else None,
            'a_unit_per_rpm': shift_a[i]['unit_per_rpm'] if i < len(shift_a) else None,
            'a_effeciency': shift_a[i]['effeciency'] if i < len(shift_a) else None,

            'b_loom': shift_b[i]['loom'] if i < len(shift_b) else None,
            'b_sizing_name': shift_b[i]['sizing_name'] if i < len(shift_b) else None,
            'b_rpm': shift_b[i]['rpm'] if i < len(shift_b) else None,
            'b_unit_per_rpm': shift_b[i]['unit_per_rpm'] if i < len(shift_b) else None,
            'b_effeciency': shift_b[i]['effeciency'] if i < len(shift_b) else None,

            'c_loom': shift_c[i]['loom'] if i < len(shift_c) else None,
            'c_sizing_name': shift_c[i]['sizing_name'] if i < len(shift_c) else None,
            'c_rpm': shift_c[i]['rpm'] if i < len(shift_c) else None,
            'c_unit_per_rpm': shift_c[i]['unit_per_rpm'] if i < len(shift_c) else None,
            'c_effeciency': shift_c[i]['effeciency'] if i < len(shift_c) else None,
        }
        merged_rows.append(row)

    return merged_rows
