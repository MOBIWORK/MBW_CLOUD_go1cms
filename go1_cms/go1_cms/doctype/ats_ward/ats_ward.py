# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Ward(Document):
    def default_list_data():
        columns = [
            {
                'label': 'Ward ID',
                'type': 'Data',
                'key': 'ward_id',
                'width': '16rem'
            },
            {
                'label': 'Ward Name',
                'type': 'Data',
                'key': 'ward_name',
                'width': '16rem'
            },
            {
                'label': 'District Name',
                'type': 'Data',
                'key': 'district_id',
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
            "ward_id",
            "ward_name",
            "district_id",
            "cat_status",
            "cat_order",
            "cat_color",
            "cat_icon",
            "name"
        ]
        return {'columns': columns, 'rows': rows}
