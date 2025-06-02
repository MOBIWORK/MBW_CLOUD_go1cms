# candidate_api.py
import frappe
import json
from frappe import _
from frappe.utils import now_datetime
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def get_my_candidate_profile():
    """
    Trả về thông tin ATS_Candidate tương ứng với email đang đăng nhập.
    Yêu cầu User đã được gán role 'Candidate' và là chủ sở hữu hồ sơ.
    """
    email = frappe.session.user
    
    candidate = frappe.get_all("ATS_Candidate", 
        filters={"can_email": email}, 
        fields=["name", "can_full_name", "can_phone", "can_email", "can_avatar", "can_cv", "status", "can_id"])

    if not candidate:
        frappe.throw(_("Không tìm thấy hồ sơ ứng viên cho email này."))

    return candidate[0]


@frappe.whitelist()
def get_my_application_status():
    """
    Trả về trạng thái ứng tuyển hiện tại (status) của ứng viên.
    """
    email = frappe.session.user

    status = frappe.db.get_value("ATS_Candidate", {"can_email": email}, "status")

    if not status:
        frappe.throw(_("Không tìm thấy trạng thái ứng viên."))

    return {
        "status": status
    }


@frappe.whitelist()
def update_my_candidate_info(data):
    """
    Cho phép ứng viên cập nhật các thông tin cá nhân cơ bản.
    Chỉ cập nhật nếu là owner của hồ sơ.
    """
    
    fields = json.loads(data)
    email = frappe.session.user

    doc = frappe.get_doc("ATS_Candidate", {"can_email": email})
    
    allowed_fields = [
        "can_full_name", "can_dob", "can_gender", "can_region",
        "can_phone", "can_address", "can_other_links",
        "educationlevel_id", "institution_id", "major_id"
    ]

    for field in allowed_fields:
        if field in fields:
            setattr(doc, field, fields[field])

    doc.save(ignore_permissions=True)
    return {"success": True, "message": "Cập nhật thông tin thành công."}


@frappe.whitelist()
def upload_cv(filedata, filename):
    """
    Cho phép ứng viên upload CV mới và gắn vào hồ sơ ATS_Candidate.
    """
    
    email = frappe.session.user
    doc = frappe.get_doc("ATS_Candidate", {"can_email": email})

    _file = save_file(filename, filedata, "ATS_Candidate", doc.name, decode=True, is_private=True)
    doc.can_cv = _file.file_url
    doc.save(ignore_permissions=True)

    return {"success": True, "message": "CV đã được cập nhật.", "cv_url": _file.file_url}

@frappe.whitelist()
def get_onboarding_steps():
    """
    Trả về danh sách các bước onboarding dành cho ứng viên đang đăng nhập.
    """
    email = frappe.session.user
    candidate = frappe.get_doc("ATS_Candidate", {"can_email": email})
    return [step.as_dict() for step in candidate.candidate_onboarding_steps]


@frappe.whitelist()
def mark_onboarding_step_complete(step_name):
    """
    Đánh dấu bước onboarding là hoàn thành đối với ứng viên hiện tại.
    """
    email = frappe.session.user
    doc = frappe.get_doc("ATS_Candidate", {"can_email": email})

    for step in doc.candidate_onboarding_steps:
        if step.step_name == step_name:
            step.is_completed = 1
            step.completed_on = now_datetime()
            doc.save(ignore_permissions=True)
            return {"success": True, "message": f"Đã đánh dấu bước '{step_name}' là hoàn thành."}

    frappe.throw(f"Không tìm thấy bước '{step_name}' trong onboarding.")

