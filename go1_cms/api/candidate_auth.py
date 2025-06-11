import frappe
import frappe.utils
from frappe import _
from frappe.utils.password import check_password, update_password
from frappe.utils import get_url
import json
import base64

@frappe.whitelist(allow_guest=True, methods=['POST'])
def candidate_login():
    """
    API đăng nhập cho candidate.
    Client sẽ POST JSON { "email": "...", "password": "..." }.
    Nếu thành công, backend trả về success=True cùng thông tin cơ bản của candidate.
    Nếu thất bại, trả về success=False và thông báo lỗi.
    """
    try:
        data = frappe.local.form_dict

        email = (data.get("email") or "").strip()
        password = (data.get("password") or "").strip()

        if not email or not password:
            return {
                "success": False,
                "message": "Vui lòng điền đầy đủ email và mật khẩu."
            }

        # Kiểm tra User tồn tại và được bật
        user = frappe.db.get_value("User", {"email": email, "enabled": 1}, "name")
        if not user:
            return {
                "success": False,
                "message": "Email không tồn tại hoặc chưa được kích hoạt."
            }

        # Kiểm tra mật khẩu
        if not check_password(user, password):
            return {
                "success": False,
                "message": "Sai mật khẩu."
            }

        # Thực hiện login bằng cách set session
        frappe.local.login_manager.user = user
        frappe.local.login_manager.post_login()

        # Lấy thông tin User
        user_info = frappe.get_doc("User", user)
        
        # Lấy thêm thông tin candidate (dựa vào email vì có thể ATS_Candidate chưa có field user)
        candidate_info = {}
        try:
            # Tìm candidate theo email
            candidate_doc = frappe.get_all("ATS_Candidate",
                filters={"can_email": email},  # Sử dụng can_email thay vì user
                fields=["name", "can_full_name", "can_email", "can_phone"],
                limit_page_length=1
            )
            if candidate_doc and len(candidate_doc) > 0:
                candidate = candidate_doc[0]
                candidate_info = {
                    "candidate_id": candidate.name,
                    "full_name": candidate.can_full_name or "",
                    "email": candidate.can_email or email,
                    "phone": candidate.can_phone or ""
                }
            else:
                # Nếu không tìm thấy record ATS_Candidate, vẫn trả về thông tin cơ bản từ User
                candidate_info = {
                    "candidate_id": None,
                    "full_name": user_info.full_name or user_info.first_name or "",
                    "email": email,
                    "phone": ""
                }
        except Exception:
            # Trong trường hợp query lỗi thì bỏ qua, chỉ trả info cơ bản
            candidate_info = {
                "candidate_id": None,
                "full_name": user_info.full_name or user_info.first_name or "",
                "email": email,
                "phone": ""
            }

        # Trả về success và thông tin cần thiết
        return {
            "success": True,
            "message": "Đăng nhập thành công!",
            "data": {
                "user": {
                    "name": user,
                    "full_name": candidate_info.get("full_name"),
                    "email": candidate_info.get("email"),
                    "phone": candidate_info.get("phone")
                },
                "candidate_id": candidate_info.get("candidate_id")
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "candidate_login")
        return {
            "success": False,
            "message": f"Đã có lỗi xảy ra: {str(e)}"
        }
        
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True, methods=['GET'])
def get_candidate_info():
    """
    API trả về thông tin Candidate đã đăng nhập.
    Nếu user chưa đăng nhập (hoặc session hết hạn), trả về success=False.
    Nếu đã đăng nhập, trả về success=True và data cơ bản của candidate.
    """
    try:
        # Kiểm tra xem đã có user trong session chưa
        user = frappe.session.user or ""
        if not user or user == "Guest":
            return {
                "success": False,
                "message": "Chưa đăng nhập hoặc phiên làm việc đã hết hạn."
            }

        # Lấy thông tin user (bảng User)
        try:
            user_doc = frappe.get_doc("User", user)
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "message": "User không tồn tại trong hệ thống."
            }

        # Lấy candidate thông qua email (cột can_email của ATS_Candidate)
        candidate_info = {}
        email = user_doc.email or ""
        if email:
            # Tìm bản ghi ATS_Candidate theo can_email = email
            candidate_rec = frappe.get_all(
                "ATS_Candidate",
                filters={"can_email": email},
                fields=["name", "can_full_name", "can_email", "can_phone"],
                limit_page_length=1
            )
            if candidate_rec and len(candidate_rec) > 0:
                c = candidate_rec[0]
                candidate_info = {
                    "candidate_id": c.name,
                    "full_name": c.can_full_name or "",
                    "email": c.can_email or email,
                    "phone": c.can_phone or ""
                }
            else:
                # Nếu không tìm thấy bản ghi trong ATS_Candidate, trả về thông tin cơ bản từ User
                candidate_info = {
                    "candidate_id": None,
                    "full_name": (user_doc.full_name or user_doc.first_name or "").strip(),
                    "email": email,
                    "phone": ""
                }
        else:
            # Nếu user_doc.email không tồn tại, trả về fallback
            candidate_info = {
                "candidate_id": None,
                "full_name": (user_doc.full_name or user_doc.first_name or "").strip(),
                "email": "",
                "phone": ""
            }

        return {
            "success": True,
            "message": "Lấy thông tin ứng viên thành công.",
            "data": {
                "user": {
                    "name": user_doc.name,
                    "full_name": candidate_info.get("full_name"),
                    "email": candidate_info.get("email"),
                    "phone": candidate_info.get("phone")
                },
                "candidate_id": candidate_info.get("candidate_id")
            }
        }

    except Exception as e:
        # Ghi log lỗi để kiểm tra nếu có exception khác
        frappe.log_error(frappe.get_traceback(), "get_candidate_info")
        return {
            "success": False,
            "message": f"Đã có lỗi xảy ra: {str(e)}"
        }

# go1_cms/api/candidate_auth.py

@frappe.whitelist()
def invite_candidate(email, full_name):
    """
    Tạo token từ email + full_name, rồi gửi link invite cho ứng viên.
    Nếu User đã tồn tại (enabled), sẽ không tạo, không gửi email nữa.
    Trả về {"success": True/False, "message": "...", "link": "..."}.
    """
    try:
        email = (email or "").strip()
        full_name = (full_name or "").strip()
        if not email or not full_name:
            return {"success": False, "message": "Cần email và họ tên."}

        # 0. Nếu user đã tồn tại và enabled, không cần gửi mail nữa
        existing_user = frappe.db.exists("User", {"email": email, "enabled": 1})
        if existing_user:
            return {
                "success": False,
                "message": "Người dùng đã có tài khoản. Không cần gửi lại email mời."
            }

        # 1. Tạo payload và encode thành Base64 (URL-safe)
        payload = {"email": email, "full_name": full_name}
        json_str = json.dumps(payload, ensure_ascii=False)
        token_bytes = base64.urlsafe_b64encode(json_str.encode("utf-8"))
        token = token_bytes.decode("utf-8")

        # 2. Xây link tạo mật khẩu
        base = get_url()  # ví dụ: https://your-domain.com
        link = f"{base}/create-password?token={token}"

        # 3. Gửi email cho ứng viên (có thể thay đổi template tuỳ ý)
        frappe.sendmail(
            recipients=email,
            subject="Mời bạn tạo mật khẩu tài khoản Candidate",
            message=f"""
                <p>Chào {full_name},</p>
                <p>Chúng tôi đã nhận hồ sơ của bạn. Vui lòng <a href="{link}">nhấn vào đây để tạo mật khẩu</a> 
                cho tài khoản Candidate của bạn.</p>
                <p>Nếu link không hoạt động, bạn có thể copy/paste đường link dưới đây vào thanh địa chỉ:</p>
                <p>{link}</p>
                <br>
                <p>Trân trọng,</p>
                <p>Phòng Tuyển dụng</p>
            """,
            reference_doctype="User",
            reference_name=None,
            now=True
        )

        return {"success": True, "message": "Email mời đã được gửi.", "link": link}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "invite_candidate")
        return {"success": False, "message": f"Có lỗi xảy ra: {str(e)}"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def setup_candidate_password():
    """
    API để ứng viên tạo tài khoản lần đầu.
    POST form-urlencoded: { "token": "...", "password": "...", "confirm_password": "..." }
    Token ở đây chính là Base64 JSON chứa {"email":..., "full_name": ...}.
    """
    try:
        data = frappe.local.form_dict
        token = (data.get("token") or "").strip()
        password = (data.get("password") or "").strip()
        confirm_password = (data.get("confirm_password") or "").strip()

        # 1. Kiểm tra token và mật khẩu
        if not token:
            return {"success": False, "message": "Token không hợp lệ hoặc bị thiếu."}
        if not password or not confirm_password:
            return {"success": False, "message": "Vui lòng nhập đủ mật khẩu và xác nhận mật khẩu."}
        if password != confirm_password:
            return {"success": False, "message": "Mật khẩu xác nhận không khớp."}
        if len(password) < 6:
            return {"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự."}

        # 2. Giải mã token (Base64 → JSON → dict)
        try:
            decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            info = json.loads(decoded)
            email = (info.get("email") or "").strip()
            full_name = (info.get("full_name") or "").strip()
        except Exception:
            return {"success": False, "message": "Token không hợp lệ hoặc đã bị thay đổi."}

        if not email:
            return {"success": False, "message": "Thông tin email không hợp lệ."}

        # 3. Kiểm tra xem user đã tồn tại chưa
        existing_user = frappe.db.exists("User", {"email": email})
        if existing_user:
            user_doc = frappe.get_doc("User", existing_user)
            if user_doc.enabled:
                return {"success": False, "message": "Tài khoản đã tồn tại. Vui lòng thử đăng nhập."}
            else:
                # Xóa user disabled (nếu có) để tạo mới
                frappe.delete_doc("User", existing_user, force=True)

        # 4. Tạo User mới
        first_name = full_name.strip().split(" ")[0] if full_name else email.split("@")[0]
        new_user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "middle_name": "",
            "last_name": full_name,
            "enabled": 1,
            "user_type": "Website User"
        })
        new_user.insert(ignore_permissions=True)

        # 5. Gán role “Candidate”
        new_user.add_roles("Candidate")

        # 6. Thiết lập mật khẩu thông qua frappe.db.set_password
        update_password(user=new_user.name, new_password=password)
        

        return {
            "success": True,
            "message": "Tạo tài khoản và mật khẩu thành công! Vui lòng đăng nhập bằng email và mật khẩu vừa tạo."
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "setup_candidate_password")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}


@frappe.whitelist()
def send_password_setup_email(email):
    """
    Tìm ATS_Candidate theo email, lấy full_name, rồi gọi invite_candidate.
    Nếu đã có User enabled với email này thì sẽ không gửi mail.
    """
    try:
        email = (email or "").strip()
        if not email:
            return {"success": False, "message": "Email trống."}

        # 1. Kiểm tra User đã tồn tại chưa
        existing_user = frappe.db.exists("User", {"email": email, "enabled": 1})
        if existing_user:
            return {"success": False, "message": "Người dùng đã có tài khoản, không gửi email mời lại."}

        # 2. Thử lấy hồ sơ ATS_Candidate mới nhất của email đó
        cand = frappe.get_all(
            "ATS_Candidate",
            filters={"can_email": email},
            fields=["can_full_name"],
            order_by="creation desc",
            limit_page_length=1
        )
        if not cand:
            return {"success": False, "message": "Không tìm thấy hồ sơ ứng viên với email này."}

        full_name = cand[0].get("can_full_name") or ""

        # 3. Gọi invite_candidate
        result = invite_candidate(email, full_name)
        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "send_password_setup_email")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}

@frappe.whitelist(allow_guest=True, methods=["POST"])
def candidate_logout():
    """
    Đăng xuất user hiện tại (Candidate).
    Xóa session cookie, commit database, trả về success để frontend redirect.
    """
    try:
        # Gọi đúng logout của login_manager
        if hasattr(frappe.local, "login_manager"):
            frappe.local.login_manager.logout()

        # Đảm bảo commit để session thực sự bị xóa
        frappe.db.commit()

        return {"success": True, "message": "Đăng xuất thành công."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "candidate_logout")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def candidate_forgot_password(email):
    """
    Gửi email “Quên mật khẩu” cho Candidate.
    Khi gọi { "email": "..." }, hàm sẽ tìm ATS_Candidate theo email, sinh token và gửi link reset.
    """
    try:
        email = (email or "").strip()
        if not email:
            return {"success": False, "message": "Vui lòng nhập địa chỉ email."}

        # 1. Tìm ATS_Candidate gần nhất có can_email = email
        cand = frappe.get_all(
            "ATS_Candidate",
            filters={"can_email": email},
            fields=["can_full_name"],
            order_by="creation desc",
            limit_page_length=1
        )
        if not cand:
            return {"success": False, "message": "Không tìm thấy hồ sơ ứng viên với email này."}

        full_name = cand[0].get("can_full_name") or ""

        # 2. Tạo token Base64 chứa email + full_name
        payload = {"email": email, "full_name": full_name}
        json_str = json.dumps(payload, ensure_ascii=False)
        token_bytes = base64.urlsafe_b64encode(json_str.encode("utf-8"))
        token = token_bytes.decode("utf-8")

        # 3. Xây link reset (sử dụng chung create-password hoặc reset-password)
        base = get_url()  # Ví dụ: https://your-domain.com
        reset_link = f"{base}/reset-password?token={token}"

        # 4. Gửi email cho ứng viên
        frappe.sendmail(
            recipients=email,
            subject="Yêu cầu đặt lại mật khẩu – Candidate",
            message=f"""
                <p>Chào {full_name},</p>
                <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản Candidate của bạn.</p>
                <p>Vui lòng <a href="{reset_link}">nhấn vào đây để đặt lại mật khẩu</a>.</p>
                <p>Nếu link trên không hoạt động, bạn có thể sao chép và dán đường link sau vào trình duyệt:</p>
                <p>{reset_link}</p>
                <br>
                <p>Trân trọng,</p>
                <p>Phòng Tuyển dụng</p>
            """,
            reference_doctype="User",
            reference_name=None,
            now=True
        )

        return {"success": True, "message": "Email đặt lại mật khẩu đã được gửi."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "candidate_forgot_password")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}


    
@frappe.whitelist(allow_guest=True, methods=["POST"])
def candidate_reset_password(token, password, confirm_password):
    """
    API đặt lại mật khẩu cho Candidate.
    - Client POST form-urlencoded: { "token": "...", "password": "...", "confirm_password": "..." }
    - Token là Base64 JSON chứa {"email": "...", "full_name": "..."} do candidate_forgot_password tạo ra.
    """
    try:
        # 1. Kiểm tra token + mật khẩu
        token = (token or "").strip()
        password = (password or "").strip()
        confirm_password = (confirm_password or "").strip()

        if not token:
            return {"success": False, "message": "Token không hợp lệ hoặc bị thiếu."}
        if not password or not confirm_password:
            return {"success": False, "message": "Vui lòng nhập mật khẩu và xác nhận mật khẩu."}
        if password != confirm_password:
            return {"success": False, "message": "Mật khẩu xác nhận không khớp."}
        if len(password) < 6:
            return {"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự."}

        # 2. Giải mã token (Base64 → JSON → dict)
        try:
            decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            info = json.loads(decoded)
            email = (info.get("email") or "").strip()
        except Exception:
            return {"success": False, "message": "Token không hợp lệ hoặc đã bị thay đổi."}

        if not email:
            return {"success": False, "message": "Email không hợp lệ trong token."}

        # 3. Tìm User đã tồn tại với email & enabled
        user_name = frappe.db.get_value("User", {"email": email, "enabled": 1}, "name")
        if not user_name:
            return {"success": False, "message": "Không tìm thấy tài khoản ứng viên nào với email này."}

        # 4. Cập nhật mật khẩu qua hàm update_password
        update_password(user_name, password)

        return {"success": True, "message": "Đặt lại mật khẩu thành công! Vui lòng đăng nhập."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "candidate_reset_password")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}

@frappe.whitelist(allow_guest=False, methods=["POST"])
def candidate_change_password(current_password, new_password, confirm_password):
    """
    API đổi mật khẩu cho Candidate đã đăng nhập.
    - Client POST form-urlencoded: { "current_password": "...", "new_password": "...", "confirm_password": "..." }
    - Phải gọi với session (credentials: include).
    """
    try:
        # 1. Kiểm tra đầu vào
        current_password = (current_password or "").strip()
        new_password = (new_password or "").strip()
        confirm_password = (confirm_password or "").strip()

        if not current_password or not new_password or not confirm_password:
            return {"success": False, "message": "Vui lòng nhập đầy đủ các trường."}
        if new_password != confirm_password:
            return {"success": False, "message": "Mật khẩu mới và xác nhận không khớp."}
        if len(new_password) < 6:
            return {"success": False, "message": "Mật khẩu mới phải có ít nhất 6 ký tự."}

        # 2. Kiểm tra user hiện tại
        user = frappe.session.user
        if not user or user == "Guest":
            return {"success": False, "message": "Bạn cần đăng nhập để đổi mật khẩu."}

        # 3. Kiểm tra mật khẩu cũ có đúng không
        #    check_password trả về True nếu đúng, False ngược lại
        if not check_password(user, current_password):
            return {"success": False, "message": "Mật khẩu cũ không chính xác."}

        # 4. Cập nhật mật khẩu mới
        update_password(user, new_password)

        return {"success": True, "message": "Đổi mật khẩu thành công!"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "candidate_change_password")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}


