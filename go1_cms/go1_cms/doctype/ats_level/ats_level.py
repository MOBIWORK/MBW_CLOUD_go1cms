# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Level(Document):
	def default_list_data():
		columns = [
			{
				'label': 'Level ID',
				'type': 'Data',
				'key': 'level_id',
				'width': '16rem'
			},
			{
				'label': 'Level Name',
				'type': 'Data',
				'key': 'level_name',
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
				'label': 'Cat Status',
				'type': 'Select',
				'key': 'cat_status',
				'width': '16rem'
			}
		]

		rows = [
			"level_id",
			"level_name",
			"level_description",
			"unit_id",
			"cat_status",
			"cat_order",
			"cat_color",
			"cat_icon",
			"name"
		]
		return {'columns': columns, 'rows': rows}

