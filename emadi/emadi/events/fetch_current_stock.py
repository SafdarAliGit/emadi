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
            # Validate that the batch exists and matches the item
            batch_item = frappe.db.get_value("Batch", set_no, "item")
            if batch_item != item_code:
                frappe.throw(f"Batch {set_no} does not belong to item {item_code}")
            
            batch_qty = frappe.db.get_value("Batch", set_no, "batch_qty")
            # Return the batch quantity
            return batch_qty or 0

        else:
            # Fetch latest qty and valuation rate from Stock Ledger Entry
            # More robust query that ensures we get the actual current stock
            result = frappe.db.sql(
                """
                SELECT qty_after_transaction AS current_stock,
                       valuation_rate as rate
                FROM `tabStock Ledger Entry`
                WHERE item_code = %s 
                  AND warehouse = %s 
                  AND is_cancelled = 0
                ORDER BY posting_date DESC, posting_time DESC
                LIMIT 1
                """,
                (item_code, warehouse),
                as_dict=True
            )
            
            if result:
                return {
                    "current_stock": result[0].get("current_stock", 0),
                    "rate": result[0].get("rate", 0)
                }
            else:
                return {
                    "current_stock": 0,
                    "rate": 0
                }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in fetch_current_stock")
        frappe.throw(f"Failed to fetch stock: {str(e)}")