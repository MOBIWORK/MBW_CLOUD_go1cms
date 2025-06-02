from frappe.utils.password import update_password
import frappe, uuid
from frappe.utils import now_datetime, add_to_date

def create_candidate_user(email, full_name):
    # Check nếu user đã tồn tại
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "enabled": 0,  # Chưa kích hoạt
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)

    # Tạo token tạm để tạo mật khẩu
    token = str(uuid.uuid4())
    expiry = add_to_date(now_datetime(), minutes=30)

    # Lưu vào custom field hoặc child DocType
    frappe.db.set_value("User", email, {
        "reset_token": token,
        "reset_token_expiry": expiry
    })

    return f"{frappe.utils.get_url()}/candidate/set-password?token={token}"
