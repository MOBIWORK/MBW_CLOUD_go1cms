# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet


class ATS_Unit(NestedSet):
	def default_list_data():
		columns = [
			{
				'label': 'Unit Name',
				'type': 'Data',
				'key': 'unit_name',
				'width': '24rem'
			},
   			{
				'label': 'Unit ID',
				'type': 'Data',
				'key': 'unit_id',
				'width': '16rem'
			},
         	{
				'label': 'Company',
				'type': 'Link',
				'key': 'company_id',
				'width': '16rem'
			},
			{
				'label': 'Cat Status',
				'type': 'Check',
				'key': 'cat_status',
				'width': '16rem'
			},
		]

		rows = [
			"unit_name",
   			"unit_id",
			"parent_ats_unit",
			"company_id",
			"unit_address",
			"unit_head",
			"unit_level",
			"is_group",
			"cat_order",
			"cat_status",
			"cat_color",
			"cat_icon",
			"name"
		]
		return {'columns': columns, 'rows': rows}
