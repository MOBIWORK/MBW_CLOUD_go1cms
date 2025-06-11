import frappe
from frappe import _
import json

# Replace missing mbw_ats functions with local implementations
def get_fields_meta(doctype):
    """Get meta fields for doctype"""
    try:
        meta = frappe.get_meta(doctype)
        return {
            "fields": [{"fieldname": f.fieldname, "label": f.label, "fieldtype": f.fieldtype} 
                      for f in meta.fields if not f.hidden]
        }
    except Exception:
        return {"fields": []}

def get_assigned_users(doctype, name):
    """Get assigned users for a document"""
    try:
        return frappe.get_all("ToDo", 
                            filters={"reference_type": doctype, "reference_name": name, "status": "Open"},
                            fields=["allocated_to"], 
                            pluck="allocated_to")
    except Exception:
        return []
        

@frappe.whitelist()
def get_detail(name):
    lst = frappe.qb.DocType("ATS_JobOpening")

    query = frappe.qb.from_(lst).select("*").where(lst.name == name).limit(1)

    lst_data = query.run(as_dict=True)
    if not len(lst_data):
        frappe.throw(_("Record not found"), frappe.DoesNotExistError)
    lst_data = lst_data.pop()

    lst_data["doctype"] = "ATS_JobOpening"
    lst_data["fields_meta"] = get_fields_meta("ATS_JobOpening")
    lst_data["_assign"] = get_assigned_users("ATS_JobOpening", name)
    
    # 🔹 Truy vấn bảng con recruitment_process
    recruitment_process = frappe.get_all(
        "Job_Opening_Rounds",
        filters={"parent": name},
        fields=["name", "round_name", "round_type", "idx"],
        order_by="idx asc"
    )
    lst_data["recruitment_process"] = recruitment_process

    # 🔹 Truy vấn bảng con hiring_committee
    hiring_committee = frappe.get_all(
        "Hiring Committee",
        filters={"parent": name},
        fields=["*"],
        order_by="idx asc"
    )
    lst_data["hiring_committee"] = hiring_committee

    return lst_data


@frappe.whitelist()
def update_record(jobOpeningId, data):
    # Kiểm tra jobOpeningId có tồn tại
    if not frappe.db.exists("ATS_JobOpening", jobOpeningId):
        frappe.throw(_("Job Opening ID {0} không tồn tại.").format(jobOpeningId))

    # Lấy bản ghi hiện tại
    doc = frappe.get_doc("ATS_JobOpening", jobOpeningId)

    # Cập nhật dữ liệu từ `data`
    for key, value in data.items():
        if key in doc.as_dict():  # Chỉ cập nhật các trường hợp lệ
            setattr(doc, key, value)

    # Lưu và commit thay đổi
    doc.save()
    frappe.db.commit()

    return {"message": "Cập nhật thành công.", "doc": doc.as_dict()}

def update_candidate_count(job_opening_id):
    """
    Cập nhật số lượng ATS_Candidate ứng tuyển vào ATS_JobOpening khi có thay đổi.
    """
    if job_opening_id:  # Sử dụng job_opening_id thay vì doc.job_opening_id
        count = frappe.db.count("ATS_Candidate", filters={"job_opening_id": job_opening_id})
        frappe.db.set_value("ATS_JobOpening", job_opening_id, "applicants_applied", count)
        
@frappe.whitelist()
def get_schedules_by_job(name):
    """Lấy tất cả lịch trình thuộc về một Job Opening cụ thể."""
    if not name:
        return {"error": "Missing required parameter: name"}

    schedules = frappe.get_all(
        "ATS_Schedule",
        filters={"jo_id": name},
        fields=[
            "name", "sch_interview_type", "sch_interview_date",
            "sch_start_time", "sch_duration", "jo_id", "can_id", "sch_room"
        ],
    )

    return {"data": schedules}

@frappe.whitelist()
def get_candidate_counts(job_opening):
    if not job_opening:
        return {"error": _("Missing job_opening parameter")}

    # Lấy danh sách các vòng tuyển dụng của tin tuyển dụng
    recruitment_stages = frappe.get_all(
        "Job_Opening_Rounds",
        filters={"parent": job_opening},  # `parent` trỏ về ATS_JobOpening
        fields=["round_name"],
        order_by="idx asc"  # Sắp xếp theo thứ tự đã thiết lập
    )

    if not recruitment_stages:
        return {"error": _("No recruitment stages found for this job opening")}

    # Truy vấn danh sách ứng viên kèm trạng thái bằng ORM
    candidate_counts = frappe.db.sql(
    """
    SELECT status, COUNT(DISTINCT name) as count
    FROM `tabCandidate Stages`
    WHERE job_opening = %s
    GROUP BY status
    """,
    (job_opening,),
    as_dict=True
)
    
    print(">>>>>>>>>>>>>>>>>>>>>>", candidate_counts)

    # Convert kết quả thành dictionary {status: count}
    status_counts = {row["status"]: row["count"] for row in candidate_counts}

    # Tạo mảng kết quả, đảm bảo mọi vòng đều có count (dù = 0)
    result = [
        {
            "stage": stage["round_name"],
            "count": status_counts.get(stage["round_name"], 0)
        }
        for stage in recruitment_stages
    ]

    return result

def delete_invalid_candidate_stages():
    # Lấy danh sách các `parent` hợp lệ từ `tabCandidate`
    valid_parents = frappe.get_all("ATS_Candidate", pluck="name")

    # Xóa các bản ghi trong `tabCandidate Stages` không có `parent` hợp lệ
    deleted_count = frappe.db.delete(
        "Candidate Stages",
        {"parent": ("not in", valid_parents)}
    )

    frappe.db.commit()  # Đảm bảo thay đổi được lưu vào DB
    print(f"Deleted {deleted_count} invalid records from `tabCandidate Stages`.")
    
@frappe.whitelist()
def get_recruitment_stages(job_opening):
    if not job_opening:
        return []
    
    # Lấy danh sách vòng tuyển dụng của tin tuyển dụng
    stages = frappe.get_all(
        "Job_Opening_Rounds",
        filters={"parent": job_opening},  # `parent` trỏ về `ATS_JobOpening`
        fields=["round_name"],
        order_by="idx asc"
    )

    return [stage["round_name"] for stage in stages]  # Trả về danh sách tên vòng tuyển dụng


@frappe.whitelist()
def add_hiring_committee_member(data):
    """
    Tạo bản ghi mới trong bảng con Hiring Committee.
    Check nếu user đã tồn tại trong ATS_JobOpening hiện tại thì không thêm.
    """
    import json

    data = json.loads(data)

    user = data.get("user")
    parent = data.get("parent")

    # Kiểm tra trùng user trong cùng parent
    exists = frappe.db.exists("Hiring Committee", {
        "parent": parent,
        "parenttype": "ATS_JobOpening",
        "parentfield": "hiring_committee",
        "user": user,
    })

    if exists:
        return {"status": "exists", "message": _("User already exists in the hiring committee for this job opening.")}

    doc = frappe.get_doc({
        "name": data.get("name"),
        "doctype": "Hiring Committee",
        "user": user,
        "parent": parent,
        "parenttype": "ATS_JobOpening",
        "parentfield": "hiring_committee",
        "idx": data.get("idx"),
        "notify_on_new_candidate": data.get("notify_on_new_candidate", 0),
        "can_view_offer_letter_details": data.get("can_view_offer_letter_details", 0)
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success"}



@frappe.whitelist()
def update_hiring_committee_member(data):
    """
    Cập nhật bản ghi con trong bảng Hiring Committee
    - Truyền lên: name, và các trường muốn cập nhật
    """
    import json

    data = json.loads(data)
    name = data.get("name")

    if not name:
        frappe.throw("Missing child record name")

    fields_to_update = {}

    for field in ["notify_on_new_candidate", "can_view_offer_letter_details"]:
        if field in data:
            fields_to_update[field] = data[field]

    if fields_to_update:
        frappe.db.set_value("Hiring Committee", name, fields_to_update)

    return {"status": "success"}

@frappe.whitelist()
def delete_hiring_committee_member(name):
    """
    Xoá bản ghi bảng con 'Hiring Committee' bằng cách gỡ nó khỏi doc cha (ATS_JobOpening)
    """
    # Truy vấn lấy bản ghi con để biết parent
    child = frappe.get_doc("Hiring Committee", name)
    parent = frappe.get_doc(child.parenttype, child.parent)

    # Lọc lại danh sách để loại bỏ bản ghi có name = name
    new_list = [
        row for row in parent.get(child.parentfield)
        if row.name != name
    ]

    parent.set(child.parentfield, new_list)
    parent.save()
    frappe.db.commit()

    return {"status": "deleted"}


