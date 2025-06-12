import frappe
import frappe.utils
from frappe import _
from frappe.utils.password import check_password
from frappe.utils import get_url
import json

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
    Tạo User với reset password key, rồi gửi link invite cho ứng viên.
    Sử dụng workflow tương tự reset password của Frappe core.
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

        # 1. Tạo hoặc lấy User (disabled) để có thể generate reset key
        user_name = None
        existing_disabled = frappe.db.exists("User", {"email": email, "enabled": 0})
        if existing_disabled:
            user_name = existing_disabled
        else:
            # Tạo user mới disabled trước
            from frappe.utils import random_string
            first_name = full_name.strip().split(" ")[0] if full_name else email.split("@")[0]
            
            new_user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "last_name": full_name,
                "enabled": 1,  # Tạo disabled trước
                "user_type": "Website User",
                "new_password": random_string(10),
                "send_welcome_email": 0
            })
            new_user.flags.ignore_permissions = True
            new_user.flags.no_welcome_mail = True
            new_user.flags.ignore_password_policy = True
            new_user.insert()
            new_user.add_roles("Candidate")
            user_name = new_user.name

        # 2. Generate reset password key sử dụng logic của Frappe nhưng tự build link
        user_doc = frappe.get_doc("User", user_name)
        
        # Sử dụng logic generate key của Frappe (copy từ reset_password method)
        from frappe.utils import get_url
        from frappe.utils.data import sha256_hash
        from frappe.utils import now_datetime
        
        key = frappe.generate_hash()
        hashed_key = sha256_hash(key)
        user_doc.db_set("reset_password_key", hashed_key)
        user_doc.db_set("last_reset_password_key_generated_on", now_datetime())
        
        # Tự build link tùy chỉnh đến frontend của bạn (không phải /update-password của Frappe)
        base_url = get_url()
        link = f"{base_url}/create-password?key={key}"  # Frontend route tùy chỉnh của bạn

        # 3. Gửi email với link reset password
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
            reference_name=user_name,
            now=True
            
        )
        
        print("link", link)

        return {"success": True, "message": "Email mời đã được gửi.", "link": link}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "invite_candidate")
        return {"success": False, "message": f"Có lỗi xảy ra: {str(e)}"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def setup_candidate_password():
    """
    API để ứng viên tạo tài khoản lần đầu.
    POST form-urlencoded: { "key": "...", "password": "...", "confirm_password": "..." }
    Key ở đây chính là reset password key của Frappe core.
    """
    try:
        data = frappe.local.form_dict
        key = (data.get("key") or "").strip()
        password = (data.get("password") or "").strip()
        confirm_password = (data.get("confirm_password") or "").strip()

        # 1. Kiểm tra key và mật khẩu
        if not key:
            return {"success": False, "message": "Key không hợp lệ hoặc bị thiếu."}
        if not password or not confirm_password:
            return {"success": False, "message": "Vui lòng nhập đủ mật khẩu và xác nhận mật khẩu."}
        if password != confirm_password:
            return {"success": False, "message": "Mật khẩu xác nhận không khớp."}
        if len(password) < 6:
            return {"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự."}

        # 2. Verify key và lấy user sử dụng Frappe core function
        from frappe.core.doctype.user.user import _get_user_for_update_password
        result = _get_user_for_update_password(key, None)
        
        if result.get("message"):
            return {"success": False, "message": result.get("message")}
        
        user_name = result.get("user")
        if not user_name:
            return {"success": False, "message": "Key không hợp lệ hoặc đã hết hạn."}

        # 3. Lấy user và kích hoạt nếu đang disabled
        user_doc = frappe.get_doc("User", user_name)
        if not user_doc.enabled:
            user_doc.enabled = 1
            user_doc.flags.no_welcome_mail = True
            user_doc.save(ignore_permissions=True)
            # Đảm bảo có role Candidate
            user_doc.add_roles("Candidate")

        # 4. Sử dụng API core của Frappe để cập nhật mật khẩu an toàn 
        from frappe.core.doctype.user.user import _update_password
        _update_password(user_name, password, logout_all_sessions=0)
        
        # 5. Clear reset password key (tương tự như core API)
        frappe.db.set_value("User", user_name, "reset_password_key", "")
        frappe.db.commit()

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
    Gửi email "Quên mật khẩu" cho Candidate.
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

        # 2. Tìm User của email này và generate reset key bằng logic Frappe
        user_name = frappe.db.get_value("User", {"email": email, "enabled": 1}, "name")
        if not user_name:
            return {"success": False, "message": "Không tìm thấy tài khoản với email này."}
        
        # Generate reset key sử dụng logic Frappe (copy từ reset_password method)
        from frappe.utils import get_url
        from frappe.utils.data import sha256_hash  
        from frappe.utils import now_datetime
        
        key = frappe.generate_hash()
        hashed_key = sha256_hash(key)
        frappe.db.set_value("User", user_name, "reset_password_key", hashed_key)
        frappe.db.set_value("User", user_name, "last_reset_password_key_generated_on", now_datetime())

        # 3. Xây link reset đến frontend tùy chỉnh của bạn
        base = get_url()
        reset_link = f"{base}/reset-password?key={key}"  # Frontend route tùy chỉnh

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
def candidate_reset_password(key, password, confirm_password):
    """
    API đặt lại mật khẩu cho Candidate.
    - Client POST form-urlencoded: { "key": "...", "password": "...", "confirm_password": "..." }
    - Key là reset password key của Frappe core.
    """
    try:
        # 1. Kiểm tra key + mật khẩu
        key = (key or "").strip()
        password = (password or "").strip()
        confirm_password = (confirm_password or "").strip()

        if not key:
            return {"success": False, "message": "Key không hợp lệ hoặc bị thiếu."}
        if not password or not confirm_password:
            return {"success": False, "message": "Vui lòng nhập mật khẩu và xác nhận mật khẩu."}
        if password != confirm_password:
            return {"success": False, "message": "Mật khẩu xác nhận không khớp."}
        if len(password) < 6:
            return {"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự."}

        # 2. Verify key và lấy user sử dụng Frappe core function
        from frappe.core.doctype.user.user import _get_user_for_update_password
        result = _get_user_for_update_password(key, None)
        
        if result.get("message"):
            return {"success": False, "message": result.get("message")}
        
        user_name = result.get("user")
        if not user_name:
            return {"success": False, "message": "Key không hợp lệ hoặc đã hết hạn."}

        # 3. Kiểm tra user enabled
        user_enabled = frappe.db.get_value("User", user_name, "enabled")
        if not user_enabled:
            return {"success": False, "message": "Tài khoản đã bị vô hiệu hóa."}

        # 4. Sử dụng API core của Frappe để cập nhật mật khẩu an toàn
        from frappe.core.doctype.user.user import _update_password
        _update_password(user_name, password, logout_all_sessions=0)
        
        # 5. Clear reset password key (tương tự như core API)
        frappe.db.set_value("User", user_name, "reset_password_key", "")
        frappe.db.commit()

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

        # 4. Sử dụng API core của Frappe để cập nhật mật khẩu an toàn
        from frappe.core.doctype.user.user import _update_password
        _update_password(user, new_password, logout_all_sessions=0)

        return {"success": True, "message": "Đổi mật khẩu thành công!"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "candidate_change_password")
        return {"success": False, "message": f"Đã có lỗi xảy ra: {str(e)}"}

@frappe.whitelist(allow_guest=True)
def test_invite_candidate():
    """
    Hàm test để debug invite_candidate function
    """
    try:
        # Test data
        test_email = "test.candidate@example.com"
        test_full_name = "Nguyễn Test Candidate"
        
        print(f"=== TESTING INVITE_CANDIDATE ===")
        print(f"Email: {test_email}")
        print(f"Full Name: {test_full_name}")
        
        # 1. Cleanup existing test user nếu có
        existing_user = frappe.db.exists("User", {"email": test_email})
        if existing_user:
            print(f"Deleting existing test user: {existing_user}")
            frappe.delete_doc("User", existing_user, force=True)
            frappe.db.commit()
        
        # 2. Test invite_candidate function
        print("Calling invite_candidate...")
        result = invite_candidate(test_email, test_full_name)
        
        print(f"Result: {result}")
        
        # 3. Kiểm tra User có được tạo không
        created_user = frappe.db.exists("User", {"email": test_email})
        print(f"User created: {created_user}")
        
        if created_user:
            user_doc = frappe.get_doc("User", created_user)
            print(f"User enabled: {user_doc.enabled}")
            print(f"User type: {user_doc.user_type}")
            print(f"Reset key exists: {bool(user_doc.reset_password_key)}")
            print(f"Roles: {[role.role for role in user_doc.roles]}")
        
        # 4. Kiểm tra email queue
        try:
            email_queue = frappe.get_all(
                "Email Queue",
                filters={"recipient": test_email},
                fields=["name", "status", "sender", "creation"],
                order_by="creation desc",
                limit_page_length=1
            )
        except Exception as e:
            print(f"Email queue query error: {str(e)}")
            email_queue = []
        
        print(f"Email queue entries: {len(email_queue)}")
        if email_queue:
            print(f"Latest email: {email_queue[0]}")
        
        # 5. Kiểm tra email settings
        email_account = frappe.get_all("Email Account", fields=["name", "email_id", "enable_outgoing"])
        print(f"Email accounts: {email_account}")
        
        # 6. Check system settings
        outgoing_email = frappe.db.get_single_value("Email Account", "default_outgoing")
        print(f"Default outgoing email: {outgoing_email}")
        
        return {
            "success": True,
            "result": result,
            "user_created": bool(created_user),
            "email_queue_count": len(email_queue),
            "email_accounts": email_account
        }
        
    except Exception as e:
        print(f"ERROR in test: {frappe.get_traceback()}")
        return {
            "success": False,
            "error": str(e),
            "traceback": frappe.get_traceback()
        }

@frappe.whitelist(allow_guest=True)
def test_email_settings():
    """
    Hàm test để kiểm tra email configuration
    """
    try:
        print("=== TESTING EMAIL SETTINGS ===")
        
        # 1. Check Email Account
        email_accounts = frappe.get_all(
            "Email Account", 
            fields=["name", "email_id", "enable_outgoing", "default_outgoing", "smtp_server", "smtp_port"]
        )
        print(f"Email Accounts: {email_accounts}")
        
        # 2. Check default outgoing
        default_outgoing = frappe.db.get_single_value("Email Account", "default_outgoing")
        print(f"Default outgoing: {default_outgoing}")
        
        # 3. Check system settings  
        try:
            site_name = frappe.db.get_single_value("Website Settings", "site_name")
            print(f"Site name: {site_name}")
        except Exception as e:
            print(f"Site name error: {str(e)}")
            site_name = None
        
        # 4. Test simple sendmail
        print("Testing simple sendmail...")
        try:
            frappe.sendmail(
                recipients="test@example.com",
                subject="Test Email from Debug",
                message="<p>This is a test email to check if sendmail works.</p>",
                now=True
            )
            print("✅ Sendmail executed without error")
        except Exception as e:
            print(f"❌ Sendmail error: {str(e)}")
        
        # 5. Check email queue after test
        try:
            recent_emails = frappe.get_all(
                "Email Queue",
                fields=["name", "recipient", "status", "error", "creation"],
                order_by="creation desc",
                limit_page_length=5
            )
            print(f"Recent emails in queue: {recent_emails}")
        except Exception as e:
            print(f"Recent emails query error: {str(e)}")
            recent_emails = []
        
        return {
            "success": True,
            "email_accounts": email_accounts,
            "default_outgoing": default_outgoing,
            "recent_emails": recent_emails
        }
        
    except Exception as e:
        print(f"ERROR in email test: {frappe.get_traceback()}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True) 
def cleanup_test_user():
    """
    Cleanup test user sau khi test xong
    """
    try:
        test_email = "test.candidate@example.com"
        existing_user = frappe.db.exists("User", {"email": test_email})
        if existing_user:
            frappe.delete_doc("User", existing_user, force=True)
            frappe.db.commit()
            return {"success": True, "message": f"Deleted test user: {existing_user}"}
        else:
            return {"success": True, "message": "No test user found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


