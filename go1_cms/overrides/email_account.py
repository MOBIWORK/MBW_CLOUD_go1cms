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
			"email_id",
			"email_account_name",
			"domain",
			"service",
			"auth_method",
			"backend_app_flow",
			"authorize_api_access",
			"password",
			"awaiting_password",
			"ascii_encode_password",
			"connected_app",
			"connected_user",
			"login_id_is_different",
			"login_id",
			"enable_incoming",
			"default_incoming",
			"use_imap",
			"use_ssl",
			"use_starttls",
			"email_server",
			"incoming_port",
			"attachment_limit",
			"email_sync_option",
			"initial_sync_count",
			"imap_folder",
			"append_emails_to_sent_folder",
			"sent_folder_name",
			"append_to",
			"create_contact",
			"enable_automatic_linking",
			"notify_if_unreplied",
			"unreplied_for_mins",
			"send_notification_to",
			"enable_outgoing",
			"use_tls",
			"use_ssl_for_outgoing",
			"smtp_server",
			"smtp_port",
			"default_outgoing",
			"always_use_account_email_id_as_sender",
			"always_use_account_name_as_sender_name",
			"send_unsubscribe_message",
			"track_email_status",
			"no_smtp_authentication",
			"always_bcc",
			"add_signature",
			"signature",
			"enable_auto_reply",
			"auto_reply_message",
			"footer",
			"brand_logo",
			"uidvalidity",
			"uidnext",
			"no_failed"
		]
		return {'columns': columns, 'rows': rows}
		