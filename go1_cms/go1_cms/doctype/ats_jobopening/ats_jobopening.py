# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator


class ATS_JobOpening(WebsiteGenerator):
	def default_list_data():
		columns = [
			{
				"label": "Public Title",
				"type": "Data",
				"key": "jo_public_title",
				"width": "20rem"
			},
			{
				"label": "Applicants Applied",
				"type": "Int",
				"key": "applicants_applied",
				"width": "10rem"
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
				"width": "16rem"
			},
			{
				"label": "Work Form",
				"type": "Select",
				"key": "jo_work_form",
				"width": "9rem"
			},
			{
				"label": "Application Deadline",
				"type": "Date",
				"key": "jo_application_deadline",
				"width": "10rem"
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
			"can_com_id",
			"name"
		]

		return {"columns": columns, "rows": rows}

	website = frappe._dict(
		template="go1_cms/templates/generators/job_opening.html",
		condition_field="publish",
		page_title_field="jo_public_title",
	)

	def validate(self):
		if not self.route or not self.route.startswith('tuyen-dung/'):
			self.route = f"tuyen-dung/{frappe.scrub(self.jo_public_title).replace('_', '-')}"

		super().validate()

	def get_context(self, context):
		context.doc_name = self.name
		context.meta_title = self.jo_public_title
		context.metatags = frappe._dict({
			"description": self.cms_meta_description or '',
			"keywords": self.cms_meta_keywords or '',
			"og:title": self.cms_meta_title or '',
			"og:description": self.cms_meta_description or '',
			"og:image": self.cms_meta_image or '',
		})

		if not self.route.endswith('jobs-123-jobs-456-jobs'):
			web_client = frappe.db.get_value(
				'MBW Client Website', {"type_web": "Live version"}, pluck='name', as_dict=1)
			if web_client:
				web_item = frappe.db.get_value('MBW Client Website Item', {
					'parent': web_client, 'parentfield': 'page_websites', 'page_type': 'Trang chi tiết tuyển dụng'}, ['page_id'], as_dict=1)

				if web_item and frappe.db.exists('Web Page Builder', web_item.page_id, cache=True):
					doc_wpb = frappe.get_doc(
						'Web Page Builder', web_item.page_id)
					doc_wpb.get_context(context)
		else:
			web_test = frappe.db.exists('Web Page Builder', {
				'route': 'jobs-123-jobs-456-jobs'}, cache=True)
			if web_test:
				doc_wpb = frappe.get_doc(
					'Web Page Builder', web_test)
				doc_wpb.get_context(context)