# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Profession(Document):
	def default_list_data():
		columns = [
			{
				'label': 'Profession ID',
				'type': 'Data',
				'key': 'profession_id',
				'width': '16rem'
			},
			{
				'label': 'Profession Name',
				'type': 'Data',
				'key': 'profession_name',
				'width': '16rem'
			},
			{
				'label': 'Using Unit',
				'type': 'Data',
				'key': 'unit_id',
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
			"profession_id",
			"profession_name",
			"profession_description",
			"unit_id",
			"cat_status",
			"cat_order",
			"cat_color",
			"cat_icon",
			"name"
		]
		return {'columns': columns, 'rows': rows}

