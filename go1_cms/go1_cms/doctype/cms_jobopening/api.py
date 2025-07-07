import frappe
from frappe import _
import json
from go1_cms.api.doc import get_fields_meta, get_assigned_users

@frappe.whitelist()
def get_detail(name):
    lst = frappe.qb.DocType("CMS_JobOpening")

    query = frappe.qb.from_(lst).select("*").where(lst.name == name).limit(1)

    lst_data = query.run(as_dict=True)
    if not len(lst_data):
        frappe.throw(_("Record not found"), frappe.DoesNotExistError)
    lst_data = lst_data.pop()

    lst_data["doctype"] = "CMS_JobOpening"
    lst_data["fields_meta"] = get_fields_meta("CMS_JobOpening")
    lst_data["_assign"] = get_assigned_users("CMS_JobOpening", name)
    
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

def update_candidate_count(job_opening_id):
    """
    Cập nhật số lượng CMS_Candidate ứng tuyển vào CMS_JobOpening khi có thay đổi.
    """
    if job_opening_id:  # Sử dụng job_opening_id thay vì doc.job_opening_id
        count = frappe.db.count("CMS_Candidate", filters={"job_opening_id": job_opening_id})
        frappe.db.set_value("CMS_JobOpening", job_opening_id, "applicants_applied", count)