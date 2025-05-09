import frappe
from frappe.model.document import Document


@frappe.whitelist()
def create_sizing_program_from_weaving_contract(weaving_contract):
    # Fetch the Weaving Contract document
    contract = frappe.get_doc("Weaving Contract", weaving_contract)
    # sp = frappe.db.get_value("Sizing Program", {"weaving_contract": weaving_contract}, "name")
    # sp_doc = None
    # if sp:
    #     sp_doc = frappe.get_doc("Sizing Program", sp)
    # if sp_doc and sp_doc.docstatus != 2:
    #     frappe.throw(f"Sizing Program already created for {weaving_contract} Weaving Contract")
    # Create a new Sizing Program
    sizing_program = frappe.new_doc("Sizing Program")
    sizing_program.weaving_contract = weaving_contract  # Link back to Weaving Contract
    sizing_program.weaver = contract.weaver  # Link back to Weaving Contract
    sizing_program.fabric_construction = contract.construction
    
    brand = None
    yarn_count = None
    for i in contract.bom_items:
        if i.get("for") == "Warp":  # Assuming 'for' is stored in 'for_value' field
            brand = i.brand
            yarn_count = i.yarn_count
            break  
    sizing_program.item = brand
    sizing_program.yarn_count = float(yarn_count[:2])
 

    # Return the Sizing Program name to open in the form view
    return sizing_program
