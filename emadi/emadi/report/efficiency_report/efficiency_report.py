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
        {"label": "Transaction ID", "fieldname": "parent", "fieldtype": "Link", "options": "Loom Production", "width": 150},

        # Shift A columns
        {"label": "Loom", "fieldname": "a_loom", "fieldtype": "Data", "width": 120},
        {"label": "Quality Name", "fieldname": "a_sizing_name", "fieldtype": "Data", "width": 140},
        {"label": "RPM", "fieldname": "a_rpm", "fieldtype": "Data", "width": 80},
        {"label": "Unit per RPM", "fieldname": "a_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Efficiency", "fieldname": "a_effeciency", "fieldtype": "Data", "width": 100},
        {"label": "Actual Reading", "fieldname": "a_actual_reading", "fieldtype": "Data", "width": 100},
        {"label": "Meters", "fieldname": "a_meters", "fieldtype": "Data", "width": 100},
        

        # Shift B columns
        {"label": "Loom", "fieldname": "b_loom", "fieldtype": "Data", "width": 120},
        {"label": "Quality Name", "fieldname": "b_sizing_name", "fieldtype": "Data", "width": 140},
        {"label": "RPM", "fieldname": "b_rpm", "fieldtype": "Data", "width": 80},
        {"label": "Unit per RPM", "fieldname": "b_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Efficiency", "fieldname": "b_effeciency", "fieldtype": "Data", "width": 100},
        {"label": "Actual Reading", "fieldname": "b_actual_reading", "fieldtype": "Data", "width": 100},
        {"label": "Meters", "fieldname": "b_meters", "fieldtype": "Data", "width": 100},
        

        # Shift C columns
        {"label": "Loom", "fieldname": "c_loom", "fieldtype": "Data", "width": 120},
        {"label": "Quality Name", "fieldname": "c_sizing_name", "fieldtype": "Data", "width": 140},
        {"label": "RPM", "fieldname": "c_rpm", "fieldtype": "Data", "width": 80},
        {"label": "Unit per RPM", "fieldname": "c_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Efficiency", "fieldname": "c_effeciency", "fieldtype": "Data", "width": 100},
        {"label": "Actual Reading", "fieldname": "c_actual_reading", "fieldtype": "Data", "width": 100},
        {"label": "Meters", "fieldname": "c_meters", "fieldtype": "Data", "width": 100},
        

        # Stats columns
        {"label": "Unit per RPM", "fieldname": "stats_unit_per_rpm", "fieldtype": "Data", "width": 110},
        {"label": "Efficiency", "fieldname": "stats_effeciency", "fieldtype": "Data", "width": 100},
        {"label": "Actual Reading", "fieldname": "stats_actual_reading", "fieldtype": "Data", "width": 100},
        {"label": "Meters", "fieldname": "stats_meters", "fieldtype": "Data", "width": 100},
        
    ]
    return columns



def get_merged_looms_data(start_date, end_date):

    def fetch_shift_data(shift):
        return frappe.db.sql("""
            SELECT d.parent, d.loom, d.sizing_name, d.rpm, round(d.unit_per_rpm,2) as unit_per_rpm,
                   round(d.effeciency,2) as effeciency, round(d.meters,2) as meters,round(d.actual_reading,2) as actual_reading
            FROM `tabLoom Production Items` d
            JOIN `tabLoom Production` m ON d.parent = m.name
            WHERE m.shift = %(shift)s
              AND m.date BETWEEN %(start_date)s AND %(end_date)s
        """, {"shift": shift, "start_date": start_date, "end_date": end_date}, as_dict=True)

    shift_a = fetch_shift_data("Shift-A")
    shift_b = fetch_shift_data("Shift-B")
    shift_c = fetch_shift_data("Shift-C")

    def to_dict_by_loom(shift_data):
        return {str(row['loom']): row for row in shift_data}

    def get_summary(shift_data):
        total_meters = sum(float(row['meters'] or 0) for row in shift_data)
        avg_eff = round(sum(float(row['effeciency'] or 0) for row in shift_data) / len(shift_data), 2) if shift_data else 0
        return total_meters, avg_eff

    def get_combined_stats(*shifts):
        combined = []
        for shift in shifts:
            combined.extend(shift)
        sum_unit_per_rpm = sum(float(row['unit_per_rpm'] or 0) for row in combined)
        avg_eff = round(sum(float(row['effeciency'] or 0) for row in combined) / len(combined), 0) if combined else 0
        sum_meters = sum(float(row['meters'] or 0) for row in combined)
        sum_actual_reading = sum(float(row['actual_reading'] or 0) for row in combined)
        return sum_unit_per_rpm, avg_eff, sum_meters,sum_actual_reading

    a_looms = to_dict_by_loom(shift_a)
    b_looms = to_dict_by_loom(shift_b)
    c_looms = to_dict_by_loom(shift_c)

    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    all_looms = sorted(set(a_looms.keys()) | set(b_looms.keys()) | set(c_looms.keys()), key=natural_sort_key)

    merged_rows = []

    # Header row
    merged_rows.append({
        'parent': '',

        'a_loom': '<b style="color: green;text-align: center;">----</b>',
        'a_sizing_name': '<b style="color: green;text-align: center;">----</b>',
        'a_rpm': '<b style="color: green;text-align: center;">----</b>',
        'a_unit_per_rpm': '<b style="color: green;text-align: center;">Shift - A</b>',
        'a_effeciency': '<b style="color: green;text-align: center;">----</b>',
        'a_actual_reading': '<b style="color: green;text-align: center;">----</b>',
        'a_meters': '<b style="color: green;text-align: center;">----</b>',

        'b_loom': '<b style="color: orange;text-align: center;">----</b>',
        'b_sizing_name': '<b style="color: orange;text-align: center;">----</b>',
        'b_rpm': '<b style="color: orange;text-align: center;">----</b>',
        'b_unit_per_rpm': '<b style="color: orange;text-align: center;">Shift - B</b>',
        'b_effeciency': '<b style="color: orange;text-align: center;">----</b>',
        'b_actual_reading': '<b style="color: orange;text-align: center;">----</b>',
        'b_meters': '<b style="color: orange;text-align: center;">----</b>',

        'c_loom': '<b style="color: blue;text-align: center;">----</b>',
        'c_sizing_name': '<b style="color: blue;text-align: center;">----</b>',
        'c_rpm': '<b style="color: blue;text-align: center;">----</b>',
        'c_unit_per_rpm': '<b style="color: blue;text-align: center;">Shift - C</b>',
        'c_effeciency': '<b style="color: blue;text-align: center;">----</b>',
        'c_actual_reading': '<b style="color: blue;text-align: center;">----</b>',
        'c_meters': '<b style="color: blue;text-align: center;">----</b>',

        'stats_unit_per_rpm': '<b style="color: purple;text-align: center;">----</b>',
        'stats_effeciency': '<b style="color: purple;text-align: center;">STATS</b>',
        'stats_actual_reading': '<b style="color: purple;text-align: center;">----</b>',
        'stats_meters': '<b style="color: purple;text-align: center;">----</b>',
        
    })

    # Data rows
    def safe_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

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
            'a_meters': a_looms.get(loom, {}).get('meters'),
            'a_actual_reading': a_looms.get(loom, {}).get('actual_reading'),

            'b_loom': b_looms.get(loom, {}).get('loom'),
            'b_sizing_name': b_looms.get(loom, {}).get('sizing_name'),
            'b_rpm': b_looms.get(loom, {}).get('rpm'),
            'b_unit_per_rpm': b_looms.get(loom, {}).get('unit_per_rpm'),
            'b_effeciency': b_looms.get(loom, {}).get('effeciency'),
            'b_meters': b_looms.get(loom, {}).get('meters'),
            'b_actual_reading': b_looms.get(loom, {}).get('actual_reading'),

            'c_loom': c_looms.get(loom, {}).get('loom'),
            'c_sizing_name': c_looms.get(loom, {}).get('sizing_name'),
            'c_rpm': c_looms.get(loom, {}).get('rpm'),
            'c_unit_per_rpm': c_looms.get(loom, {}).get('unit_per_rpm'),
            'c_effeciency': c_looms.get(loom, {}).get('effeciency'),
            'c_meters': c_looms.get(loom, {}).get('meters'),
            'c_actual_reading': c_looms.get(loom, {}).get('actual_reading'),

            'stats_unit_per_rpm': float(a_looms.get(loom, {}).get('unit_per_rpm', 0)) + float(b_looms.get(loom, {}).get('unit_per_rpm', 0)) + float(c_looms.get(loom, {}).get('unit_per_rpm', 0)),
            'stats_effeciency': round((float(a_looms.get(loom, {}).get('effeciency', 0)) + float(b_looms.get(loom, {}).get('effeciency', 0)) + float(c_looms.get(loom, {}).get('effeciency', 0))) / 3, 0),
            'stats_meters': round(float(a_looms.get(loom, {}).get('meters', 0)) + float(b_looms.get(loom, {}).get('meters', 0)) + float(c_looms.get(loom, {}).get('meters', 0)), 2),
            'stats_actual_reading': safe_float(a_looms.get(loom, {}).get('actual_reading')) +
                       safe_float(b_looms.get(loom, {}).get('actual_reading')) +
                       safe_float(c_looms.get(loom, {}).get('actual_reading'))
        }
        merged_rows.append(row)

    # Summary row
    a_total_meters, a_avg_eff = get_summary(shift_a)
    b_total_meters, b_avg_eff = get_summary(shift_b)
    c_total_meters, c_avg_eff = get_summary(shift_c)

    stats_unit_per_rpm, stats_avg_eff, stats_meters, stats_actual_reading = get_combined_stats(shift_a, shift_b, shift_c)

    merged_rows.append({
        'parent': '<b style="color:black;">Total / Average</b>',

        'a_loom': '',
        'a_sizing_name': '',
        'a_rpm': '',
        'a_unit_per_rpm': '',
        'a_effeciency': f'<b style="color: green;">Avg: {a_avg_eff}</b>',
        'a_meters': f'<b style="color: green;">Total: {a_total_meters}</b>',

        'b_loom': '',
        'b_sizing_name': '',
        'b_rpm': '',
        'b_unit_per_rpm': '',
        'b_effeciency': f'<b style="color: orange;">Avg: {b_avg_eff}</b>',
        'b_meters': f'<b style="color: orange;">Total: {b_total_meters}</b>',

        'c_loom': '',
        'c_sizing_name': '',
        'c_rpm': '',
        'c_unit_per_rpm': '',
        'c_effeciency': f'<b style="color: blue;">Avg: {c_avg_eff}</b>',
        'c_meters': f'<b style="color: blue;">Total: {c_total_meters}</b>',

        'stats_unit_per_rpm': f'<b style="color: purple;">Total: {stats_unit_per_rpm}</b>',
        'stats_effeciency': f'<b style="color: purple;">Avg: {stats_avg_eff}</b>',
        'stats_meters': f'<b style="color: purple;">Total: {stats_meters}</b>',
        'stats_actual_reading': f'<b style="color: purple;">Total: {stats_actual_reading}</b>',
    })

    return merged_rows
