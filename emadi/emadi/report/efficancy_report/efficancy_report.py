import frappe
from collections import defaultdict
import re

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
import re

def get_merged_looms_data(start_date, end_date):
    shift_a = frappe.db.sql("""
        SELECT d.parent, d.loom, d.sizing_name, d.rpm, d.unit_per_rpm, d.effeciency
        FROM `tabLoom Production Items` d
        JOIN `tabLoom Production` m ON d.parent = m.name
        WHERE m.shift = 'Shift-A'
          AND m.date >= %(start_date)s AND m.date <= %(end_date)s
    """, {"start_date": start_date, "end_date": end_date}, as_dict=True)

    shift_b = frappe.db.sql("""
        SELECT d.parent, d.loom, d.sizing_name, d.rpm, d.unit_per_rpm, d.effeciency
        FROM `tabLoom Production Items` d
        JOIN `tabLoom Production` m ON d.parent = m.name
        WHERE m.shift = 'Shift-B'
          AND m.date >= %(start_date)s AND m.date <= %(end_date)s
    """, {"start_date": start_date, "end_date": end_date}, as_dict=True)

    shift_c = frappe.db.sql("""
        SELECT d.parent, d.loom, d.sizing_name, d.rpm, d.unit_per_rpm, d.effeciency
        FROM `tabLoom Production Items` d
        JOIN `tabLoom Production` m ON d.parent = m.name
        WHERE m.shift = 'Shift-C'
          AND m.date >= %(start_date)s AND m.date <= %(end_date)s
    """, {"start_date": start_date, "end_date": end_date}, as_dict=True)

    def to_dict_by_loom(shift_data):
        return {str(row['loom']): row for row in shift_data}

    a_looms = to_dict_by_loom(shift_a)
    b_looms = to_dict_by_loom(shift_b)
    c_looms = to_dict_by_loom(shift_c)

    # Natural alphanumeric sort key
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    # All loom keys sorted naturally
    all_looms = sorted(set(a_looms.keys()) | set(b_looms.keys()) | set(c_looms.keys()), key=natural_sort_key)

    merged_rows = []

    # Header row
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

    # Data rows
    for loom in all_looms:
        row = {
            'parent': (
                a_looms.get(loom, {}).get('parent') or
                b_looms.get(loom, {}).get('parent') or
                c_looms.get(loom, {}).get('parent')
            ),

            'a_loom': a_looms.get(loom, {}).get('loom'),
            'a_sizing_name': a_looms.get(loom, {}).get('sizing_name'),
            'a_rpm': a_looms.get(loom, {}).get('rpm'),
            'a_unit_per_rpm': a_looms.get(loom, {}).get('unit_per_rpm'),
            'a_effeciency': a_looms.get(loom, {}).get('effeciency'),

            'b_loom': b_looms.get(loom, {}).get('loom'),
            'b_sizing_name': b_looms.get(loom, {}).get('sizing_name'),
            'b_rpm': b_looms.get(loom, {}).get('rpm'),
            'b_unit_per_rpm': b_looms.get(loom, {}).get('unit_per_rpm'),
            'b_effeciency': b_looms.get(loom, {}).get('effeciency'),

            'c_loom': c_looms.get(loom, {}).get('loom'),
            'c_sizing_name': c_looms.get(loom, {}).get('sizing_name'),
            'c_rpm': c_looms.get(loom, {}).get('rpm'),
            'c_unit_per_rpm': c_looms.get(loom, {}).get('unit_per_rpm'),
            'c_effeciency': c_looms.get(loom, {}).get('effeciency'),
        }
        merged_rows.append(row)

    return merged_rows


