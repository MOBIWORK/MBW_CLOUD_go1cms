import frappe
import frappe.utils
import random
from frappe import _
import string
from mbw_ats.ultils.candidate_utils import enqueue_application_date_processing


@frappe.whitelist()
def assign_candidates_to_job(job_id, candidate_ids):
    """
    Gán danh sách candidate vào job_id. Với mỗi candidate:
    - Nếu đã có job_id rồi → clone bản ghi mới với job mới và can_id random
    - Nếu chưa có job → update trực tiếp job_opening_id và status
    - Tránh trùng email trong cùng 1 job
    - Enqueue xử lý can_application_date để tránh crash
    """
    if not job_id or not candidate_ids:
        frappe.throw(_("Missing job_id or candidate list"))

    candidate_ids = frappe.parse_json(candidate_ids)
    inserted = 0
    skipped = 0

    for can_id in candidate_ids:
        try:
            candidate = frappe.get_doc("ATS_Candidate", can_id)

            # Kiểm tra trùng email trong job
            existed = frappe.db.exists("ATS_Candidate", {
                "can_email": candidate.can_email,
                "job_opening_id": job_id
            })
            if existed:
                skipped += 1
                continue

            first_round = get_first_round_of_job(job_id)

            if not candidate.job_opening_id:
                # Update trực tiếp nếu chưa có job
                candidate.job_opening_id = job_id
                candidate.status = first_round
                # Set can_application_date cơ bản để tránh validation error
                if not candidate.can_application_date:
                    candidate.can_application_date = frappe.utils.now()
                candidate.save(ignore_permissions=True)
                
                # Enqueue xử lý application date đầy đủ
                enqueue_application_date_processing(
                    candidate_id=candidate.name,
                    job_opening_id=job_id,
                    force_update=True,
                    now=False
                )
            else:
                # Clone nếu đã có job
                new_candidate = frappe.copy_doc(candidate)
                new_candidate.name = None  # Auto-generate
                new_candidate.job_opening_id = job_id
                new_candidate.status = first_round
                new_candidate.can_id = generate_random_can_id()
                # Set can_application_date cơ bản
                new_candidate.can_application_date = frappe.utils.now()
                new_candidate.insert(ignore_permissions=True)
                
                # Enqueue xử lý application date đầy đủ cho bản sao mới
                enqueue_application_date_processing(
                    candidate_id=new_candidate.name,
                    job_opening_id=job_id,
                    force_update=True,
                    now=False
                )

            inserted += 1

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"assign_candidates_to_job Error for candidate {can_id}")
            # Tiếp tục với candidate tiếp theo thay vì crash
            continue

    return {
        "inserted": inserted,
        "skipped": skipped,
        "message": f"Đã xử lý {inserted} ứng viên, bỏ qua {skipped} ứng viên đã tồn tại"
    }


def get_first_round_of_job(job_id):
    rounds = frappe.get_all(
        "Job_Opening_Rounds",
        filters={"parent": job_id},
        fields=["round_name"],
        order_by="idx asc",
        limit_page_length=1
    )
    return rounds[0].round_name if rounds else "Ứng tuyển"


def generate_random_can_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
