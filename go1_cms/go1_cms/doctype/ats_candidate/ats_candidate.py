# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ATS_Candidate(Document):
	def default_list_data():
		columns = [
			{
				"label": "Full Name",
				"type": "Data",
				"key": "can_full_name",
				"width": "16rem"
			},
			{
				"label": "Status",
				"type": "Check",
				"key": "status",
				"width": "12rem"
			},
			{
				"label": "Phone Number",
				"type": "Data",
				"key": "can_phone",
				"width": "10rem"
			},
			{
				"label": "Email",
				"type": "Data",
				"key": "can_email",
				"width": "14rem"
			},
			{
				"label": "Job Opening",
				"type": "Link",
				"key": "job_opening_id",
				"width": "16rem"
			},
			{
				"label": "Application Date",
				"type": "Date",
				"key": "can_application_date",
				"width": "14rem"
			},
   			# {
			# 	"label": "Tags",
			# 	"type": "Data",
			# 	"key": "_user_tags",
			# 	"width": "16rem"
			# }
		]

		rows = [
			"can_id",
			"can_full_name",
			"can_phone",
			"can_email",
			"job_opening_id",
			"can_application_date",
			"candidatesource_id",
			"can_recruiter",
			"can_last_workplace",
			"can_dob",
			"can_gender",
			"can_region",
			"can_address",
			"can_other_links",
			"educationlevel_id",
			"institution_id",
			"major_id",
			"can_collaborator",
			"can_referral",
			"status",
			"_user_tags",
			"rejected",
			"name"
		]
		return {
			"columns": columns,
			"rows": rows
		}

	def before_save(self):
		if not self.status and self.job_opening_id:
			stages = get_job_opening_rounds(self.job_opening_id)
			if stages:
				round_name = stages[0].round_name
				self.status = round_name
		if not self.candidatesource_id:
			self.candidatesource_id = "Website"
@frappe.whitelist()
def get_job_opening_rounds(job_opening):
	"""
	Lấy danh sách vòng tuyển dụng của một Job Opening
	"""
	if not job_opening:
		return []

	rounds = frappe.get_all(
		"Job_Opening_Rounds",
		filters={"parent": job_opening},
		fields=["name", "round_name", "idx"],  # Thêm idx để sắp xếp
		order_by="idx asc"  # Sắp xếp theo thứ tự idx tăng dần
	)
	return rounds

def update_candidate_name(doc, method):
    new_name = f"{doc.can_id} - {doc.can_full_name}"

    # Kiểm tra nếu tên mới khác tên cũ
    if doc.name and doc.name != new_name:
        try:
            # Đổi tên bản ghi, bỏ `merge=True`
            frappe.rename_doc("ATS_Candidate", doc.name, new_name, force=True, ignore_if_exists=True)
            doc.name = new_name  # Cập nhật lại name
        except frappe.DoesNotExistError:
            frappe.log_error(f"Không tìm thấy bản ghi {doc.name} để đổi tên.", "Rename ATS_Candidate Error")
        except Exception as e:
            frappe.log_error(f"Lỗi khi đổi tên ứng viên: {str(e)}", "Rename ATS_Candidate Error")

    
    
def update_candidate_names():
    candidates = frappe.get_all("ATS_Candidate", fields=["name", "can_id", "can_full_name"])
    for candidate in candidates:
        new_name = f"{candidate.can_id} - {candidate.can_full_name}"
        if candidate.name != new_name:
            try:
                frappe.rename_doc("ATS_Candidate", candidate.name, new_name, force=True)
                print(f"Đã đổi tên: {candidate.name} -> {new_name}")
            except Exception as e:
                print(f"Lỗi khi đổi tên {candidate.name}: {e}")

def autoname(doc, method):    
    doc.name = f"{doc.can_id} - {doc.can_full_name}"