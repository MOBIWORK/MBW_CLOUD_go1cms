# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_District(Document):
    def default_list_data():
        columns = [
            {
                'label': 'District ID',
                'type': 'Data',
                'key': 'district_id',
                'width': '16rem'
            },
            {
                'label': 'District Name',
                'type': 'Data',
                'key': 'district_name',
                'width': '16rem'
            },
            {
                'label': 'Province Name',
                'type': 'Link',
                'key': 'province_id',
                'options': 'ATS_Province',
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
            "district_id",
            "district_name",
            "province_id",
            "cat_status",
            "cat_order",
            "cat_color",
            "cat_icon",
            "name"
        ]
        return {'columns': columns, 'rows': rows}
