import json
import frappe
@frappe.whitelist()
def str_to_json(json_str):
	return json.loads(json_str)
