import frappe
from frappe.model.document import Document

@frappe.whitelist()
def fetch_fabric_construction_items(quality, qty):
    """
    Fetch rows from Fabric Construction Item where parent = quality and return them.
    Calculate yarn_qty as consumption * qty.
    """
    items = frappe.get_all(
        "Fabric Construction Item",
        filters={"parent": quality},
        fields=["for", "yarn_count", "consumption"]
    )

    for item in items:
        item["yarn_qty"] = item["consumption"] * float(qty)  # Calculate yarn_qty

    return items
