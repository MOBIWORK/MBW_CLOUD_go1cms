# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_JobOpening(Document):
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
