import frappe


@frappe.whitelist()
def fetch_current_stock(item_code, warehouse):
    data = {}

    # Construct the SQL query
    sql_query = """
            SELECT
                qty_after_transaction AS current_stock
            FROM
                `tabStock Ledger Entry`
            WHERE
                item_code = %s AND warehouse = %s AND is_cancelled = 0
            ORDER BY
                posting_date DESC, posting_time DESC
            LIMIT 1
        """

    # Execute the query
    result = frappe.db.sql(sql_query, (item_code, warehouse), as_dict=True)
    return result[0].current_stock if result else 0