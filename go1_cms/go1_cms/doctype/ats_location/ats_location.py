# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ATS_Location(Document):
	def default_list_data():
		columns = [
			{
				'label': 'Location ID',
				'type': 'Data',
				'key': 'location_id',
				'width': '16rem'
			},
			{
				'label': 'Location Name',
				'type': 'Data',
				'key': 'location_name',
				'width': '16rem'
			},
			{
				'label': 'Country',
				'type': 'Link',
				'key': 'country_id',
				'options': 'ATS_Country',
				'width': '16rem'
			},
			{
				'label': 'Province',
				'type': 'Link',
				'key': 'province_id',
				'options': 'ATS_Province',
				'width': '16rem'
			},
			{
				'label': 'District',
				'type': 'Link',
				'key': 'district_id',
				'options': 'ATS_District',
				'width': '16rem'
			},
			{
				'label': 'Ward',
				'type': 'Link',
				'key': 'ward_id',
				'options': 'ATS_Ward',
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
			"location_id",
			"location_name",
			"country_id",
			"province_id",
			"district_id",
			"ward_id",
			"location_address",
			"cat_status",
			"cat_order",
			"cat_color",
			"cat_icon",
			"name"
		]
		return {'columns': columns, 'rows': rows}

