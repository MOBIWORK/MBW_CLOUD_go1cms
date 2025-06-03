import frappe
import uuid
from frappe.utils import now_datetime, add_to_date
from frappe.utils.password import update_password

@frappe.whitelist()
def apply_cv(email, full_name, phone):
    """Ứng viên apply CV, tạo User (chưa kích hoạt), sinh token"""
    # Check nếu user tồn tại
    user = frappe.db.get("User", {"email": email})
    if not user:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "phone":phone,
            "user_type": "Website User",
            "first_name": full_name,
            "enabled": 0,
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)

    # Tạo hoặc cập nhật token truy cập
    token = str(uuid.uuid4())
    expiry = add_to_date(now_datetime(), minutes=30)

    link_doc = frappe.get_doc({
        "doctype": "Candidate_Access_Link",
        "email": email,
        "token": token,
        "expiry": expiry,
        "used": 0
    })
    link_doc.insert(ignore_permissions=True)

    url = f"{frappe.utils.get_url()}/candidate/set-password?token={token}"
    return {
        "success": True,
        "set_password_url": url
    }


@frappe.whitelist(allow_guest=True)
def set_password(token, password, confirm_password):
    """Xác thực token, đặt mật khẩu, gán role và kích hoạt tài khoản"""
    if password != confirm_password:
        frappe.throw("Mật khẩu không khớp.")

    link = frappe.db.get("Candidate_Access_Link", {"token": token, "used": 0})
    if not link:
        frappe.throw("Token không hợp lệ hoặc đã được sử dụng.")

    if now_datetime() > link.expiry:
        frappe.throw("Token đã hết hạn.")

    email = link.email
    user = frappe.get_doc("User", email)

    update_password(user.name, password)
    user.enabled = 1
    user.save(ignore_permissions=True)
    # Gán role Candidate nếu chưa có
    if "Candidate" not in frappe.get_roles(user.name):
        user.add_roles("Candidate")

    # Đánh dấu token đã dùng
    frappe.db.set_value("Candidate_Access_Link", link.name, {
        "used": 1
    })

    return {
        "success": True,
        "message": "Đặt mật khẩu thành công. Bạn có thể đăng nhập."
    }

@frappe.whitelist(allow_guest=True)
def forgot_password(email):
    """
    Gửi email đặt lại mật khẩu cho ứng viên đã được kích hoạt.
    Tương tự như `/forgot` mặc định của Frappe nhưng cho phép tùy biến.
    """
    user = frappe.db.get("User", {"email": email})
    if not user:
        frappe.throw("Không tìm thấy người dùng với email này.")

    if not frappe.db.get_value("User", email, "enabled"):
        frappe.throw("Tài khoản chưa được kích hoạt. Vui lòng hoàn tất đăng ký trước.")

    # Gửi email đặt lại mật khẩu (dùng core API có sẵn)
    frappe.local.login_manager = frappe.auth.LoginManager()
    try:
        frappe.local.login_manager.reset_password(email)
        return {
            "success": True,
            "message": "Đã gửi email đặt lại mật khẩu. Vui lòng kiểm tra hộp thư đến."
        }
    except frappe.exceptions.DoesNotExistError:
        frappe.throw("Không thể gửi email khôi phục.")