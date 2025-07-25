import frappe
from frappe.model.document import Document


class DailyFabricProduction(Document):
	def on_submit(self):
		if self.daily_fabric_production_item:
			for item in self.daily_fabric_production_item:
				doc = frappe.new_doc("Fabric Production")
				doc.posting_date = self.date
				doc.posting_time = self.time
				doc.daily_fabric_production = self.name
				target_warehouse = get_target_warehouse_by_status(item.status)
				if not target_warehouse:
					frappe.throw("Target Warehouse not found for status: {0}".format(item.status))
				doc.target_warehouse = target_warehouse
				doc.qty = item.qty
				doc.fabric_item = item.fabric_item
				doc.quality = fetch_quality(item.fabric_item)

				# Append source items
				items = get_fabric_construction(item.fabric_item, item.qty)
				if items:
					for i in items:
						it = doc.append("fabric_production_item", {})
						setattr(it, "for", i.get("for"))
						setattr(it, "yarn_count", i.get("yarn_count"))
						setattr(it, "consumption", i.get("consumption"))
						setattr(it, "yarn_qty", i.get("yarn_qty"))

				try:
					doc.save()
					frappe.db.set_value("Daily Fabric Production Item", item.name, "fabric_production", doc.name)

				except Exception as e:
					frappe.throw(f"Error saving Fabric Production: {str(e)}")
			self.reload()


def get_fabric_construction(fabric_item, qty):
	fc = frappe.get_all(
		"Fabric Construction",
		filters={"fabric_item": fabric_item},
		fields=["name"],
		limit=1
	)
	name = fc[0]["name"] if fc else None

	if not name:
		return []

	items = frappe.get_all(
		"Fabric Construction Item",
		filters={"parent": name},
		fields=["for", "yarn_count", "consumption"]
	)

	for item in items:
		consumption = float(item.get("consumption") or 0)
		item["yarn_qty"] = round(consumption * float(qty), 2)

	return items


def fetch_quality(fabric_item):
	fc = frappe.get_all(
		"Fabric Construction",
		filters={"fabric_item": fabric_item},
		fields=["quality"],
		limit=1
	)
	return fc[0]["quality"] if fc else None


def get_target_warehouse_by_status(status_type=None):
    if not status_type:
        return None

    records = frappe.get_all(
        "Emadi Settings Item",
        filters={"status": status_type},
        fields=["warehouse"],
        limit=1
    )

    if records:
        return records[0].warehouse

    return None
