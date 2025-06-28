import frappe

@frappe.whitelist()
def get_linked_fields(doctype):
    if not frappe.has_permission(doctype, "read"):
        frappe.throw(("Permission Denied"), frappe.PermissionError)

    return frappe.get_all("DocField", filters={"parent": doctype, "fieldtype": "Link"}, fields=["fieldname", "options"])