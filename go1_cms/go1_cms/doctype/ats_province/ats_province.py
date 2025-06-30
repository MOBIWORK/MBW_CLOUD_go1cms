# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Province(Document):
    def default_list_data():
        columns = [
            {
                'label': 'Province ID',
                'type': 'Data',
                'key': 'province_id',
                'width': '16rem'
            },
            {
                'label': 'Province Name',
                'type': 'Data',
                'key': 'province_name',
                'width': '16rem'
            },
            {
                'label': 'Country Name',
                'type': 'Link',
                'key': 'country_id',
                'options': 'ATS_Country',
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
            "province_id",
            "province_name",
            "country_id",
            "cat_status",
            "cat_order",
            "cat_color",
            "cat_icon",
            "name"
        ]
        return {'columns': columns, 'rows': rows}

