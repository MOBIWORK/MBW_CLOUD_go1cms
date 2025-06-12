# candidate_api.py
import frappe
import json
from frappe import _
from frappe.utils import now
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
    # Get the onboarding record for the current user
    onboarding_docs = frappe.get_all("ATS_Onboarding", 
        filters={"email": email}, 
        fields=["name"],
        order_by="creation asc")
    
    if not onboarding_docs:
        return []
    
    # Get steps from the child table
    all_steps = []
    for onboarding in onboarding_docs:
        onboarding_doc = frappe.get_doc("ATS_Onboarding", onboarding.name)
        for step in onboarding_doc.steps:
            step_data = {
                "onboarding_id": onboarding.name,
                "step_name": step.step_name,
                "description": step.description,
                "is_completed": step.is_completed,
                "completed_on": step.completed_on,
                "step_type": step.step_type,
                "required_upload": step.required_upload,
                "uploaded_file": step.uploaded_file,
                "requires_hr_approval": step.requires_hr_approval,
                "approved_by_hr": step.approved_by_hr
            }
            all_steps.append(step_data)
    
    return all_steps

@frappe.whitelist()
def mark_onboarding_step_complete(onboarding_id, step_name, uploaded_file=None):
    onboarding = frappe.get_doc("ATS_Onboarding", onboarding_id)
    found = False
    target_step = None

    for step in onboarding.steps:
        if step.step_name == step_name:
            target_step = step
            found = True
            break

    if not found:
        frappe.throw(_("Step '{0}' not found in onboarding").format(step_name))

    try:
        # Cập nhật thông tin step trực tiếp trên parent doc
        target_step.is_completed = 1
        target_step.completed_on = now()
        target_step.completed_by_user = frappe.session.user
        if uploaded_file:
            target_step.uploaded_file = uploaded_file
            
        
        # Save parent document để trigger hook của ATS_Onboarding
        onboarding.save(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error saving onboarding step: {str(e)}")
        frappe.throw(_("Có lỗi xảy ra khi lưu bước onboarding: {0}").format(str(e)))

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
        is_private=0
    )

    # --- 4. Cập nhật thông tin step ---
    # Kiểm tra xem đã có file cũ chưa để xóa (optional - có thể bỏ qua để giữ lại file cũ)
    old_file_url = matched_step.uploaded_file
    is_replacement = bool(old_file_url)
    
    try:
        # Cập nhật thông tin step trực tiếp trên parent doc
        matched_step.uploaded_file = file_doc.file_url
        matched_step.is_completed = 1
        matched_step.completed_on = frappe.utils.now()
        matched_step.completed_by_user = frappe.session.user

        if matched_step.requires_hr_approval:
            matched_step.approved_by_hr = 0  # Explicitly mark as not approved
            if is_replacement:
                frappe.msgprint(_("File đã được thay thế và đang chờ HR xem xét lại."))
            else:
                frappe.msgprint(_("This step is pending HR review."))

        # Save parent document để trigger hook của ATS_Onboarding và đồng bộ sang ATS
        onboarding.save(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error saving onboarding step file: {str(e)}")
        frappe.throw(_("Có lỗi xảy ra khi lưu file onboarding: {0}").format(str(e)))

    return {
        "message": "File replaced successfully" if is_replacement else "File uploaded successfully",
        "file_url": file_doc.file_url,
        "step_name": step_name,
        "old_file_url": old_file_url if is_replacement else None,
        "is_replacement": is_replacement,
        "status": "waiting_for_hr_review" if matched_step.requires_hr_approval else "completed"
    }

@frappe.whitelist()
def get_candidate_timeline():
    """
    Lấy timeline các vòng tuyển dụng của tất cả jobs của ứng viên từ ATS_CandidateRoundHistory
    """
    email = frappe.session.user
    
    # Lấy tất cả thông tin candidate có cùng email
    candidates = frappe.get_all("ATS_Candidate", 
        filters={"can_email": email}, 
        fields=["name", "status", "can_full_name", "job_opening_id", "can_application_date"])
    
    if not candidates:
        frappe.throw(_("Không tìm thấy hồ sơ ứng viên cho email này."))
    
    all_timelines = []
    candidate_name = candidates[0]["can_full_name"]  # Lấy tên từ record đầu tiên
    
    # Kiểm tra xem có bản ghi onboarding nào không
    has_onboarding = frappe.db.exists("ATS_Onboarding", {"email": email})
    
    for candidate in candidates:
        # Lấy thông tin job opening
        job_info = frappe.get_value("ATS_JobOpening", candidate["job_opening_id"], 
                                  ["jo_public_title", "jo_position"]) if candidate["job_opening_id"] else (None, None)
        
        job_title = job_info[0] if job_info else "Không xác định"
        job_position = job_info[1] if job_info else "Không xác định"
        
        # Lấy lịch sử các vòng từ child table
        round_history = frappe.get_all("ATS_CandidateRoundHistory", 
            filters={"parent": candidate["name"]},
            fields=[
                "round_name", 
                "change_date",
                "sync_id"
            ],
            order_by="change_date asc"
        )
        
        # Thêm thông tin trạng thái dựa trên logic
        timeline_data = []
        for i, round_data in enumerate(round_history):
            # Nếu có onboarding thì tất cả các vòng đều completed
            if has_onboarding:
                status = "Completed"
                status_text = "Đã hoàn thành"
            else:
                # Logic cũ cho trường hợp chưa có onboarding
                is_current = round_data.get("round_name") == candidate["status"]
                is_completed = i < len(round_history) - 1
                
                if is_completed:
                    status = "Completed"
                    status_text = "Đã hoàn thành"
                elif is_current:
                    status = "In Progress"
                    status_text = "Đang tiến hành"
                else:
                    status = "Pending"
                    status_text = "Chờ xử lý"
            
            # Tạo object timeline với thông tin đầy đủ
            timeline_item = {
                "round_name": round_data.get("round_name"),
                "moved_to_round_date": round_data.get("change_date"),
                "status": status,
                "status_text": status_text,
                "notes": f"Chuyển vòng vào ngày {round_data.get('change_date', '')}" if round_data.get('change_date') else "Không có ghi chú",
                "round_order": i + 1
            }
            timeline_data.append(timeline_item)
        
        # Thêm timeline của job này vào danh sách
        job_timeline = {
            "job_info": {
                "job_title": job_title,
                "job_position": job_position,
                "application_date": candidate["can_application_date"],
                "current_status": candidate["status"]
            },
            "timeline": timeline_data
        }
        all_timelines.append(job_timeline)
    
    return {
        "candidate_info": {
            "full_name": candidate_name,
            "has_onboarding": bool(has_onboarding)
        },
        "job_timelines": all_timelines
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

