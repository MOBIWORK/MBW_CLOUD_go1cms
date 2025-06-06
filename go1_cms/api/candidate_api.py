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

    status,job_opening_id = frappe.db.get_value("ATS_Candidate", {"can_email": email}, ["status","job_opening_id"])
    recruitment_process = frappe.db.get_value("ATS_JobOpening", job_opening_id, "recruitment_process")
    if not status:
        frappe.throw(_("Không tìm thấy trạng thái ứng viên."))

    return {
        "status": status,
        "recruitment_process":recruitment_process
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
    email = frappe.session.user
    #candidate = frappe.get_doc("ATS_Candidate", {"can_email": email})
    steps = frappe.get_all("ATS_Onboarding", 
        filters={"email": email}, 
        fields=["name", "step_name", "description", "is_completed", "completed_on"], 
        order_by="creation asc")
    return steps

@frappe.whitelist()
def mark_onboarding_step_complete(onboarding_id, step_name, uploaded_file=None):
    onboarding = frappe.get_doc("ATS_Onboarding", onboarding_id)
    found = False

    for step in onboarding.steps:
        if step.step_name == step_name:
            step.is_completed = 1
            step.completed_on = now()
            step.completed_by_user = frappe.session.user
            if uploaded_file:
                step.uploaded_file = uploaded_file
            found = True
            break

    if not found:
        frappe.throw(_("Step '{0}' not found in onboarding").format(step_name))

    onboarding.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": "Step marked as completed",
        "step": step_name,
        "completed_by": frappe.session.user
    }

@frappe.whitelist()
def get_onboarding_summary(onboarding_id):
    onboarding = frappe.get_doc("ATS_Onboarding", onboarding_id)
    total = len(onboarding.steps)
    completed = [step.step_name for step in onboarding.steps if step.is_completed]
    incomplete = [step.step_name for step in onboarding.steps if not step.is_completed]

    return {
        "onboarding_id": onboarding.name,
        "total_steps": total,
        "completed_steps": len(completed),
        "incomplete_steps": total - len(completed),
        "completed_step_names": completed,
        "incomplete_step_names": incomplete
    }

@frappe.whitelist()
def upload_onboarding_step_file(onboarding_id, step_name):
    file = frappe.request.files.get('file')
    if not file:
        frappe.throw(_("No file found in upload"))

    onboarding = frappe.get_doc("ATS_Onboarding", onboarding_id)

    # --- 1. Kiểm tra quyền truy cập ---
    candidate_email = frappe.get_value("ATS_Candidate", onboarding.candidate, "can_email")
    if frappe.session.user != candidate_email and frappe.session.user != "Administrator":
        frappe.throw(_("You are not authorized to upload this file"))

    # --- 2. Tìm step tương ứng ---
    matched_step = None
    for step in onboarding.steps:
        if step.step_name == step_name:
            matched_step = step
            break

    if not matched_step:
        frappe.throw(_("Step '{0}' not found").format(step_name))

    if not matched_step.required_upload:
        frappe.throw(_("This step does not require a file upload"))

    # --- 3. Lưu file ---
    file_doc = save_file(
        fname=file.filename,
        content=file.stream.read(),
        dt=onboarding.doctype,
        dn=onboarding.name,
        folder="Home/Attachments",
        is_private=1
    )

    # --- 4. Cập nhật thông tin step ---
    matched_step.uploaded_file = file_doc.file_url
    matched_step.is_completed = 1
    matched_step.completed_on = frappe.utils.now()
    matched_step.completed_by_user = frappe.session.user

    if matched_step.requires_hr_approval:
        matched_step.approved_by_hr = 0  # Explicitly mark as not approved
        frappe.msgprint(_("This step is pending HR review."))

    # 5. Nếu cần HR duyệt thì gửi email
    if matched_step.requires_hr_approval:
        send_hr_approval_email(
            onboarding=onboarding,
            step_name=step_name,
            file_url=file_doc.file_url
        )

    onboarding.save(ignore_permissions=True)
    frappe.db.commit()

    

    return {
        "message": "File uploaded successfully",
        "file_url": file_doc.file_url,
        "step_name": step_name,
        "status": "waiting_for_hr_review" if matched_step.requires_hr_approval else "completed"
    }

def send_hr_approval_email(onboarding, step_name, file_url):
    hr_users = frappe.get_all("User", filters={"role_profile_name": "HR Manager"}, fields=["email"])
    if not hr_users:
        frappe.msgprint("Không tìm thấy user nào có vai trò HR Manager để gửi thông báo.")

    subject = f"[Onboarding] Ứng viên {onboarding.full_name} đã hoàn thành bước cần HR phê duyệt"
    message = f"""
    Xin chào,<br><br>

    Ứng viên <b>{onboarding.full_name}</b> ({onboarding.email}) vừa hoàn thành bước <b>{step_name}</b> trong quy trình Onboarding cho vị trí <b>{onboarding.position}</b>.<br><br>

    <b>File đính kèm:</b> <a href="{file_url}">{file_url}</a><br><br>

    Vui lòng đăng nhập vào hệ thống để xem xét và phê duyệt bước này.<br><br>

    Trân trọng,<br>
    Hệ thống ATS
    """

    recipients = [u["email"] for u in hr_users if u.get("email")]
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message
        )

