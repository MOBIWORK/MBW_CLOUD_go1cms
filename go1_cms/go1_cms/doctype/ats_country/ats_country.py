# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Country(Document):
    def default_list_data():
        columns = [
            {
                'label': 'Country ID',
                'type': 'Data',
                'key': 'country_id',
                'width': '16rem'
            },
            {
                'label': 'Country Name',
                'type': 'Data',
                'key': 'country_name',
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
            "country_id",
            "country_name",
            "cat_status",
            "cat_order",
            "cat_color",
            "cat_icon",
            "name"
        ]
        return {'columns': columns, 'rows': rows}
