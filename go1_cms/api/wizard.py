import frappe

@frappe.whitelist(allow_guest=True)
def mark_done():
    """Đánh dấu là đã bỏ qua hoặc hoàn thành hướng dẫn"""
    frappe.db.set_single_value("User Guide Settings", "hide_user_guide", 1)
    frappe.db.commit()
    return {"status": "success"}

@frappe.whitelist(allow_guest=True)
def should_show():
    """Kiểm tra xem có hiển thị hướng dẫn không"""
    hide_guide = frappe.db.get_single_value("User Guide Settings", "hide_user_guide")
    return {"show_guide": not bool(hide_guide)}