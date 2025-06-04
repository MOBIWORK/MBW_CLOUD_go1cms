# Copyright (c) 2025, mbwcloud.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from go1_cms.go1_cms.webhook.handler import safe_save

class ATS_JobOpening(Document):
	def default_list_data():
		columns = [
			{
				"label": "Public Title",
				"type": "Data",
				"key": "jo_public_title",
				"width": "16rem"
			},
			{
				"label": "Applicants Applied",
				"type": "Int",
				"key": "applicants_applied",
				"width": "12rem"
			},
			{
				"label": "Publish to Career Page",
				"type": "Check",
				"key": "publish_to_career_page",
				"width": "12rem"
			},
			{
				"label": "Status",
				"type": "Int",
				"key": "status",
				"width": "12rem"
			},
			{
				"label": "Level ID",
				"type": "Link",
				"key": "jo_level_id",
				"width": "10rem"
			},
			{
				"label": "Position",
				"type": "Link",
				"key": "jo_position",
				"width": "10rem"
			},
			{
				"label": "Work Form",
				"type": "Select",
				"key": "jo_work_form",
				"width": "12rem"
			},
			{
				"label": "Application Deadline",
				"type": "Date",
				"key": "jo_application_deadline",
				"width": "14rem"
			},
		]

		rows = [
			"jo_id",
			"jo_internal_title",
			"jo_public_title",
			"jo_level_id",
			"jo_position",
			"jo_work_form",
			"jo_application_deadline",
			"jo_contact_email",
			"jo_using_unit",
			"jo_profession_id",
			"jo_location",
			"jo_display_quantity",
			"jo_salary_display_option",
			"jo_min_salary",
			"jo_max_salary",
			"jo_currency",
			"jo_job_description",
			"jo_job_requirement",
			"jo_job_benefits",
			"jo_contact_person",
			"jo_contact_phone",
			"jo_language_requirement",
			"status",
			"applicants_applied",
			"publish_to_career_page",
			"cal_com_id",
			"name"
		]

		return {"columns": columns, "rows": rows}

	def on_update(self):
		"""Forward data sang CMS_JobOpening sau khi sync từ ATS
		"""
		meta = frappe.get_meta("CMS_JobOpening")
		skip_fieldtypes = {'Section Break', 'Column Break', 'Button'}
		skip_fieldnames = {'name', 'owner', 'sync_id','creation', 'modified', 'modified_by', 'doctype'}

		non_updatable_fields = {
			df.fieldname for df in meta.fields
			if df.read_only or df.unique or df.fieldtype in skip_fieldtypes or df.fieldname in skip_fieldnames
		}
		sync_id =self.sync_id
		job_cms = frappe.db.get_value("CMS_JobOpening",{"sync_id":sync_id})
		if job_cms:
			safe_save(non_updatable_fields,self.as_dict(),"CMS_JobOpening",sync_id)
	def after_insert(self):
		data_insert = self.as_dict()
		data_insert.pop("doctype",None)
		cms_job = frappe.get_doc({ "doctype": "CMS_JobOpening", **data_insert })
		cms_job.insert(ignore_permissions=True)
		frappe.db.commit()

	def after_delete(self):
		if self.sync_id:
			frappe.db.delete("CMS_JobOpening",{"sync_id":self.sync_id})