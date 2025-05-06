import requests
import frappe
from frappe import _
import json
import base64


"""########################### Begin Sync ATS_Candidate ###########################"""
def sync_send_candidate(doc, method):
	try:
		if not doc.sync_source:
			base_url = frappe.conf.get("mbw_ats_site_name") or ''
			api_key = frappe.conf.get("mbw_ats_api_key") or ''
			api_secret = frappe.conf.get("mbw_ats_api_secret") or ''
			if not base_url or not api_key or not api_secret:
				frappe.log_error(f"Sync send candidate failed", "Base URL, api_key, api_secret is not configured.")
				return
			api_endpoint = base_url + "/api/method/mbw_ats.api.synchronous_data.sync_receive_candidate"
			json_data = doc.as_dict()

			file_cv = {}
			if doc.can_cv:
				file_cv_name = frappe.db.get_value('File', {'file_url': doc.can_cv, 'attached_to_name': doc.name, 'attached_to_doctype': doc.doctype, 'attached_to_field': 'can_cv'}, ['name'])
				if file_cv_name:
					doc_file = frappe.get_doc('File', file_cv_name)
					file_cv = {
						"file_name": doc_file.file_name,
						"file_type": doc_file.file_type,
						"content": base64.b64encode(doc_file.get_content()).decode('utf-8')
					}
			
			res = requests.post(
				api_endpoint,
				data=frappe.as_json({
					"doc": json_data,
					"file_cv": file_cv
				}),
				headers={
					"Content-Type": "application/json",
					"Authorization": f"Token {api_key}:{api_secret}"
				}
			)

			if res.status_code != 200:
				frappe.log_error(f"Sync send candidate failed", f"Response: {res.status_code} - {res.text}")
				return
		else:
			# Làm mới lại field sync_source để cho lần sau gửi đi
			frappe.db.set_value(doc.doctype, doc.name, 'sync_source', 0)
	except Exception as e:
		frappe.log_error(f"Sync send candidate failed: {e}")


@frappe.whitelist()
def sync_receive_candidate(**kwargs):
	try:
		file_avt = frappe._dict(kwargs.get('file_avt') or {})
		data = frappe._dict(kwargs.get('doc') or {})
		
		candidate_name = frappe.db.get_value(data.doctype, {'name': data.sync_id}, ['name'])
		if candidate_name:
			# Cập nhật thông tin của ứng viên
			doc_update = frappe.get_doc(data.doctype, candidate_name)
			doc_update.can_id = data.can_id
			doc_update.can_full_name = data.can_full_name
			doc_update.can_dob = data.can_dob
			doc_update.can_gender = data.can_gender
			doc_update.can_region = data.can_region
			doc_update.sync_id = data.name
			# đánh dấu sync_source để tránh gửi lại
			doc_update.sync_source = 1
			doc_update.can_phone = data.can_phone
			doc_update.can_email = data.can_email
			doc_update.can_address = data.can_address
			doc_update.can_other_links = data.can_other_links
			doc_update.status = data.status
			doc_update.candidate_stages = data.candidate_stages or []
			doc_update.round_history = data.round_history or []
			doc_update.save(ignore_permissions=True)
			
			# xóa file đính kèm cũ
			if doc_update.can_avatar:
				file_old = frappe.db.get_value('File', {'file_url': doc_update.can_avatar, 'attached_to_name': doc_update.name, 'attached_to_doctype': doc_update.doctype, 'attached_to_field': 'can_avatar'}, ['name'])
				if file_old:
					frappe.get_doc('File', file_old)
					frappe.db.set_value(doc_update.doctype, doc_update.name, 'can_avatar', '')

			# Lưu file đính kèm mới
			if file_avt.content:
				file_doc = frappe.get_doc({
					"doctype": "File",
					"file_name": file_avt.file_name,
					"is_private": 0,
					"attached_to_doctype": doc_update.doctype,
					"attached_to_name": doc_update.name,
					"attached_to_field": 'can_avatar',
					"content": base64.b64decode(file_avt.content),
					"folder": "Home",
					"file_url": "",
				})
				file_doc.save()
				frappe.db.set_value(doc_update.doctype, doc_update.name, 'can_avatar', file_doc.file_url)

		return {
			'code': '00',
			'status': 'Success',
			'msg': 'Candidate data synchronized successfully',
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Sync receive candidate Error")
		return {
			'code': '1',
			'status': 'Error',
			'msg': "Candidate data synchronized failed",
		}

"""########################### End Sync ATS_Candidate ###########################"""