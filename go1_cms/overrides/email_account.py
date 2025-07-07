# import frappe
import frappe
from frappe import _
from frappe.email.doctype.email_account.email_account import EmailAccount

class CustomEmailAccount(EmailAccount):
	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'ID',
				'type': 'Data',
				'key': 'name',
				'width': '20rem',
			},
			{
				'label': 'Status',
				'type': 'Check',
				'key': 'default_incoming',
				'width': '16rem',
			},
			{
				'label': 'Email Address',
				'type': 'Data',
				'key': 'email_id',
				'width': '20rem',
			},
			{
				'label': 'Domain',
				'type': 'Link',
				'key': 'domain',
				'width': '20rem',
			},
			{
				'label': 'Last Modified',
				'type': 'Datetime',
				'key': 'modified',
				'width': '8rem',
			},
		]
		rows = [
			"name",
			"default_incoming",
			"email_id",
			"domain",
			"modified",
		]
		return {'columns': columns, 'rows': rows}
		