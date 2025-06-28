# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Company(Document):
	def default_list_data():
		columns = [
         	{
				'label': 'Company ID',
				'type': 'Data',
				'key': 'company_id',
				'width': '16rem'
			},
			{
				'label': 'Company Name',
				'type': 'Data',
				'key': 'company_name',
				'width': '16rem'
			},
			{
				'label': 'Company Address',
				'type': 'Data',
				'key': 'company_address',
				'width': '16rem'
			},
			{
				'label': 'Cat Status',
				'type': 'Select',
				'key': 'cat_status',
				'width': '16rem'
			},
		]

		rows = [
			"company_name",
   			"company_id",
			"company_address",
			"company_head",
			"cat_order",
            "cat_status",
			"cat_color",
			"cat_icon",
			"name"
		]
		return {'columns': columns, 'rows': rows} 