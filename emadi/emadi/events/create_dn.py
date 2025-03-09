import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_dn(weaving_contract):
    # Fetch the Weaving Contract document
    contract = frappe.get_doc("Weaving Contract", weaving_contract)

    # Check if a Delivery Note already exists and is not canceled
    existing_dn = frappe.db.get_value("Delivery Note", {"weaving_contract": weaving_contract}, "name")
    if existing_dn:
        existing_dn_doc = frappe.get_doc("Delivery Note", existing_dn)
        if existing_dn_doc.docstatus != 2:  # Not canceled
            frappe.throw(f"Delivery Note already exists for Weaving Contract {weaving_contract}: {existing_dn}")

    # Create a new Delivery Note
    delivery_note = frappe.new_doc("Delivery Note")
    delivery_note.posting_date = contract.date
    delivery_note.posting_time = contract.time
    delivery_note.currency = "PKR"
    delivery_note.customer = contract.weaver  # Ensure 'weaver' is set in Weaving Contract
    delivery_note.fabric_item = contract.construction
    delivery_note.weaving_contract = weaving_contract

    # Add BOM items if available
    
    delivery_note.append("items", {
        "item_code": "Sizing / Weaving Charges",
        "item_name":"Sizing / Weaving Charges",
        "description":"Sizing / Weaving Charges",
        "qty": 0,
        "rate": contract.total_charges_per_meter,
        "uom": "Meter",
        "stock_uom": "Meter"
    })
    
    if contract.get("bom_items"):
        for item in contract.bom_items:
            delivery_note.append("bom_items_dn", {
                "for": item.get("for"),
                "yarn_count": item.get("yarn_count"),
                "consumption": item.get("consumption"),
                "yarn_qty": 0,
                "uom": item.uom,
                "brand": item.brand
            })

    # Save and submit the Delivery Note

    return delivery_note  # Return the name to open in form view

