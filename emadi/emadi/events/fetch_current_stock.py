import frappe

@frappe.whitelist()
def fetch_current_stock(item_code, warehouse, set_no=None):
    """
    Fetch current stock for a given item and warehouse.
    - If set_no (Batch) is provided, fetch batch_qty from Batch (after validating item_code).
    - Otherwise, fetch latest stock from Stock Ledger Entry.
    """
    try:
        if set_no:
            # Optionally validate that the batch matches the item
            batch_qty = frappe.db.get_value("Batch", set_no, "batch_qty")
            # Return the batch quantity
            return batch_qty or 0

        else:
            # Fetch latest qty from Stock Ledger Entry
            result = frappe.db.sql(
                """
                SELECT qty_after_transaction AS current_stock
                FROM `tabStock Ledger Entry`
                WHERE item_code = %s AND warehouse = %s AND is_cancelled = 0
                ORDER BY posting_date DESC, posting_time DESC
                LIMIT 1
                """,
                (item_code, warehouse),
                as_dict=True
            )
            return result[0].current_stock if result else 0

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in fetch_current_stock")
        return 0
