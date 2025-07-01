# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CMS_Candidate(Document):
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
		# if not self.candidatesource_id:
		# 	self.candidatesource_id = "Website"
  
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
