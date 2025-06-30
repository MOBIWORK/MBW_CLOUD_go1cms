# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Position(Document):
    def default_list_data():
        columns = [
            {
                'label': 'Position ID',
                'type': 'Data',
                'key': 'position_id',
                'width': '16rem'
            },
            {
                'label': 'Position Name',
                'type': 'Data',
                'key': 'position_name',
                'width': '16rem'
            },
            {
                'label': 'Using Unit',
                'type': 'Link',
                'key': 'unit_id',
                'options': 'ATS_Unit',
                'width': '16rem'
            },
            {
                'label': 'Profession ID',
                'type': 'Link',
                'key': 'profession_id',
                'options': 'ATS_Profession',
                'width': '16rem'
            },
            {
                'label': 'Cat Status',
                'type': 'Select',
                'key': 'cat_status',
                'width': '16rem'
            }
        ]

        rows = [
            "position_id",
            "position_name",
            "unit_id",
            "profession_id",
            "position_description",
            "required_skills",
            "position_benefits",
            "recruitment_process_id",
            "cat_status",
            "cat_order",
            "cat_color",
            "cat_icon",
            "job_position_rounds",
            "name"
        ]
        return {'columns': columns, 'rows': rows}

