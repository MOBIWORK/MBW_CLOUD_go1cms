import frappe
import requests
from frappe import _
import json
import base64
import filetype
import time


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
			file_avt = {}
			if doc.can_avatar:
				file_avt_name = frappe.db.get_value('File', {'file_url': doc.can_avatar, 'attached_to_name': doc.name, 'attached_to_doctype': doc.doctype, 'attached_to_field': 'can_avatar'}, ['name'])
				if file_avt_name:
					doc_file = frappe.get_doc('File', file_avt_name)
					file_avt = {
						"file_name": doc_file.file_name,
						"file_type": doc_file.file_type,
						"content": base64.b64encode(doc_file.get_content()).decode('utf-8')
					}

			res = requests.post(
				api_endpoint,
				data=frappe.as_json({
					"doc": json_data,
					"file_cv": file_cv,
     				"file_avt": file_avt
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
		
		# Gọi hàm extract_cv_url để xử lý file CV
		if doc.is_upload_cv and doc.can_cv:
			file_cv = frappe.db.get_value('File', {'file_url': doc.can_cv, 'attached_to_name': doc.name, 'attached_to_doctype': doc.doctype, 'attached_to_field': 'can_cv'}, ['name'])
			if file_cv:
				frappe.db.after_commit.add(lambda: frappe.enqueue(handle_extract_cv, file_cv_name=file_cv, candidate_name=doc.name))

	except Exception as e:
		frappe.log_error(f"Sync send candidate failed: {e}")


@frappe.whitelist()
def sync_receive_candidate(**kwargs):
	try:
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


def handle_extract_cv(file_cv_name, candidate_name):
	try:
		data_extract = extract_cv_url(file_cv_name)
		if data_extract.get('error'):
			frappe.log_error("Extract CV Error", f"{data_extract}")
		else:
			data = data_extract.get('data') or {}
			if data.get('can_avatar'):
				can_avatar = data.get('can_avatar')
				# Giải mã base64 thành bytes
				file_content = base64.b64decode(can_avatar)
				# Đoán file type từ nội dung
				kind = filetype.guess(file_content)
				if kind:
					extension = kind.extension  # vd: 'pdf', 'docx'
				else:
					extension = "bin"

				# xóa file đính kèm cũ
				doc_update = frappe.get_doc("ATS_Candidate", candidate_name)
				if doc_update.can_avatar:
					file_avt_old = frappe.db.get_value('File', {'file_url': doc_update.can_avatar, 'attached_to_name': doc_update.name, 'attached_to_doctype': doc_update.doctype, 'attached_to_field': 'can_avatar'}, ['name'])
					if file_avt_old:
						frappe.delete_doc('File', file_avt_old)
						frappe.db.set_value("ATS_Candidate", candidate_name, 'can_avatar', '')

				file_name = f"cv_extracted_{int(time.time())}.{extension}"
				file_doc = frappe.get_doc({
					"doctype": "File",
					"file_name": file_name,
					"is_private": 0,
					"attached_to_doctype": "ATS_Candidate",
					"attached_to_name": candidate_name,
					"attached_to_field": 'can_avatar',
					"content": file_content,
					"folder": "Home",
					"file_url": "",
				})
				file_doc.save()
				frappe.db.set_value("ATS_Candidate", candidate_name, {
					'can_avatar': file_doc.file_url,
					'is_upload_cv': 0
				})
				doc_update.reload()
				doc_update.save(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Handle extract cv Error")


def rename_keys(data, rename_map):
    return {rename_map.get(k, k): v for k, v in data.items()}
def rename_keys_in_list(data_list, rename_map):
    return [{rename_map.get(k, k): v for k, v in item.items()} for item in data_list]

def extract_cv_url(file_cv_name):
	url_extract_ai = "https://taskingai.mbwcloud.com/v2/genai/hr-assistants/cv-extraction/pdf-upload"

	headers = {
		"Authorization": "Bearer tkoBjKTFTNfFDzkmGe0z9ppUusIeexVy",
		"topcv_assistant_id": "X5lMjLOTtqJ0v14yj8zix3vT",
		"other_assistant_id": "X5lMoK7W2Q87cb1sYg3liuXY",
	}

	try:
		file_doc = frappe.get_doc("File", file_cv_name)
		files = {
			"file": (file_doc.file_name, file_doc.get_content(), "application/pdf")
		}
		response = requests.post(url_extract_ai, files=files, headers=headers)

		if response.status_code == 200:
			data = frappe.parse_json(response.json())

			if "personal_info" in data.data:
				personal_info = {
					"name": "can_full_name",
					"email": "can_email",
					"phone": "can_phone"
				}
				data.data["personal_info"] = rename_keys(data.data["personal_info"], personal_info)

			if "work_experience" in data.data:
				work_experience = {
					"company": "work_experience_place",
					"position": "work_experience_role",
					"start_date": "work_experience_start",
					"end_date": "work_experience_end",
					"descriptions": "work_experience_detail"
				}
				data.data["work_experience"] = rename_keys_in_list(data.data["work_experience"], work_experience)

			if "projects" in data.data:
				projects = {
					"name": "projects_name",
					"tasks": "project_description",
					"start_date": "project_start_date",
					"end_date": "project_end_date",
					"position": "project_role"
				}
				data.data["projects"] = rename_keys_in_list(data.data["projects"], projects)

			if "skills" in data.data:
				skill = {
					"name": "can_skill_name",
				}
				data.data["skills"] = rename_keys_in_list(data.data["skills"], skill)

			# Xử lý ảnh avatar nếu có
			if "list_imgs_base64" in data and data["list_imgs_base64"]:
				data.data['can_avatar'] = data['list_imgs_base64'][0]
				del data['list_imgs_base64']
			else:
				data.data['can_avatar'] = None

			return data
		else:
			frappe.log_error(f"CV Upload API Error {response.status_code}: {response.text}", "CV Upload API")
			return {
				"error": "CV extraction failed",
				"status_code": response.status_code,
				"response": response.text
			}

	except frappe.DoesNotExistError:
		return {
			"error": "File not found",
			"file_name": file_cv_name
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "CV Upload API")
		return {
			"error": "Unhandled error occurred while processing the CV.",
			"details": str(e)
		}

"""########################### End Sync ATS_Candidate ###########################"""

"""########################### Begin Sync ATS_JobOpening ###########################"""
def sync_send_jobopening(doc, method):
	try:
		if not doc.sync_source:
			base_url = frappe.conf.get("mbw_ats_site_name") or ''
			api_key = frappe.conf.get("mbw_ats_api_key") or ''
			api_secret = frappe.conf.get("mbw_ats_api_secret") or ''
			if not base_url or not api_key or not api_secret:
				frappe.log_error(f"Sync send job opening failed", "Base URL, api_key, api_secret is not configured.")
				return
			api_endpoint = base_url + "/api/method/mbw_ats.api.synchronous_data.sync_receive_jobopening"
			json_data = doc.as_dict()

			# Gửi dữ liệu bao gồm cả thông tin bảng con
			res = requests.post(
				api_endpoint,
				data=frappe.as_json({
					"doc": json_data
				}),
				headers={
					"Content-Type": "application/json",
					"Authorization": f"Token {api_key}:{api_secret}"
				}
			)

			if res.status_code != 200:
				frappe.log_error(f"Sync send job opening failed", f"Response: {res.status_code} - {res.text}")
				return
		else:
			# Làm mới lại field sync_source để cho lần sau gửi đi
			frappe.db.set_value(doc.doctype, doc.name, 'sync_source', 0)

	except Exception as e:
		frappe.log_error(f"Sync send job opening failed: {e}")

@frappe.whitelist()
def sync_receive_jobopening(**kwargs):
	try:
		# Extract data and operation from kwargs
		data = frappe._dict(kwargs.get('doc') or {})
		operation = kwargs.get('operation', 'update')  # Default to update if not specified
		
		# Debug logging
		frappe.logger("sync").debug(f"Received sync request for job opening {data.get('name')} with operation {operation}")
		
		# Ghi log chi tiết dữ liệu nhận được cho debug
		frappe.log_error(
			message=f"Received job opening data: {data.get('name')}, recruitment_process: {len(data.get('recruitment_process', []))}, hiring_committee: {len(data.get('hiring_committee', []))}",
			title="Sync Debug - Received JobOpening"
		)
		
		# Check if we have valid data
		if not data or not data.get('name'):
			error_msg = "Missing required data for job opening sync"
			frappe.logger("sync").error(error_msg)
			frappe.log_error(error_msg, "Sync Receive JobOpening Error")
			return {
				'code': '1',
				'status': 'Error',
				'msg': error_msg,
			}
		
		frappe.logger("sync").info(f"Processing {operation} for job opening {data.get('name')} from mbw_ats")
		
		# Handle deletion operation
		if operation == 'delete':
			job_opening_name = frappe.db.get_value('ATS_JobOpening', {'sync_id': data.name}, ['name'])
			if job_opening_name:
				try:
					doc = frappe.get_doc('ATS_JobOpening', job_opening_name)
					# Set flag to prevent triggering sync back
					doc.flags.ignore_sync = True
					doc.delete(ignore_permissions=True)
					frappe.logger("sync").info(f"Successfully deleted job opening {job_opening_name}")
					return {
						'code': '00',
						'status': 'Success',
						'msg': f'Job opening {job_opening_name} deleted successfully',
					}
				except Exception as e:
					error_msg = f"Failed to delete job opening {job_opening_name}: {str(e)}"
					frappe.logger("sync").error(error_msg)
					frappe.log_error(frappe.get_traceback(), error_msg)
					return {
						'code': '1',
						'status': 'Error',
						'msg': error_msg,
					}
			else:
				return {
					'code': '00',
					'status': 'Success',
					'msg': 'Job opening not found, nothing to delete',
				}
		
		# Set sync_source to mark this as coming from mbw_ats (prevents sync loops)
		data.sync_source = 1
		
		# Better searching for existing records using multiple criteria
		# Check if job opening exists by sync_id (primary way to find record)
		job_opening_by_sync_id = frappe.db.get_value('ATS_JobOpening', {'sync_id': data.name}, ['name'])
		
		# Check if job opening exists by name (direct ID match)
		job_opening_by_name = None
		if frappe.db.exists("ATS_JobOpening", data.name):
			job_opening_by_name = data.name
		
		# Check if job opening exists by jo_id
		job_opening_by_jo_id = None
		if data.get('jo_id'):
			job_opening_by_jo_id = frappe.db.get_value('ATS_JobOpening', {'jo_id': data.jo_id}, ['name'])
		
		# Determine which record to update based on all checks
		job_opening_name = job_opening_by_sync_id or job_opening_by_name or job_opening_by_jo_id
		
		if job_opening_name:
			# Update existing job opening
			try:
				frappe.logger("sync").info(f"Found existing job opening {job_opening_name}, updating it")
				doc_update = frappe.get_doc("ATS_JobOpening", job_opening_name)
				
				# Fields to update
				fields_to_sync = [
					"jo_id", "jo_public_title", "jo_internal_title", "jo_level_id", 
					"jo_profession_id", "jo_work_form", "jo_display_quantity",
					"jo_language_requirement", "publish_to_career_page", "jo_using_unit", 
					"jo_position", "jo_location", "jo_application_deadline", "status", 
					"applicants_applied", "jo_job_description", "jo_job_requirement", 
					"jo_job_benefits", "jo_contact_phone", "jo_contact_email",
					"jo_contact_person", "jo_currency", "jo_salary_display_option", 
					"jo_min_salary", "jo_max_salary"
				]
				
				# Update fields
				for field in fields_to_sync:
					if hasattr(data, field) and getattr(data, field) is not None:
						setattr(doc_update, field, getattr(data, field))
				
				# Keep sync flags
				doc_update.sync_id = data.name
				doc_update.sync_source = 1
				
				# Debug log child table data
				frappe.logger("sync").debug(f"Child tables in received data: recruitment_process={len(data.get('recruitment_process', []))}, hiring_committee={len(data.get('hiring_committee', []))}")
				
				# LƯU Ý QUAN TRỌNG: Sử dụng đúng tên bảng con "recruitment_process" (không phải job_opening_rounds)
				
				# Xử lý bảng recruitment_process - xóa và thêm lại từ dữ liệu mới
				if hasattr(doc_update, "recruitment_process"):
					frappe.logger("sync").debug(f"Clearing recruitment_process table for {doc_update.name}")
					doc_update.recruitment_process = []
				
				if hasattr(data, "recruitment_process") and isinstance(data.recruitment_process, list) and data.recruitment_process:
					frappe.logger("sync").debug(f"Adding {len(data.recruitment_process)} recruitment process records")
					for round_data in data.recruitment_process:
						if isinstance(round_data, dict):
							# Xử lý trường automation_rules để tránh lỗi giới hạn kích thước
							automation_rules = round_data.get("automation_rules", "")
							if automation_rules and len(automation_rules) > 255:  # Giả sử giới hạn là 255 ký tự
								automation_rules = automation_rules[:255]
								frappe.logger("sync").warning(f"Truncated automation_rules for round {round_data.get('round_name')} due to length constraints")
							
							doc_update.append("recruitment_process", {
								"round_name": round_data.get("round_name"),
								"round_type": round_data.get("round_type"),
								"position": round_data.get("position"),
								"default": round_data.get("default"),
								"test_link": round_data.get("test_link", "")
								# Không đồng bộ trường automation_rules
							})
				
				# Xử lý bảng hiring_committee - xóa và thêm lại từ dữ liệu mới
				if hasattr(doc_update, "hiring_committee"):
					frappe.logger("sync").debug(f"Clearing hiring_committee table for {doc_update.name}")
					doc_update.hiring_committee = []
				
				if hasattr(data, "hiring_committee") and isinstance(data.hiring_committee, list) and data.hiring_committee:
					frappe.logger("sync").debug(f"Adding {len(data.hiring_committee)} hiring_committee members")
					for member_data in data.hiring_committee:
						if isinstance(member_data, dict):
							doc_update.append("hiring_committee", {
								"user": member_data.get("user"),
								"notify_on_new_candidate": member_data.get("notify_on_new_candidate"),
								"can_view_offer_letter_details": member_data.get("can_view_offer_letter_details")
							})
				
				# Set flag to prevent triggering sync back
				doc_update.flags.ignore_sync = True
				
				# Save the document
				doc_update.save(ignore_permissions=True)
				
				frappe.logger("sync").info(f"Updated job opening {doc_update.name} from sync operation")
				
				return {
					'code': '00',
					'status': 'Success',
					'msg': 'Job opening updated successfully',
					'job_opening_name': doc_update.name
				}
			except Exception as e:
				error_msg = f"Failed to update job opening {job_opening_name}: {str(e)}"
				frappe.logger("sync").error(error_msg)
				frappe.log_error(frappe.get_traceback(), error_msg)
				return {
					'code': '1',
					'status': 'Error',
					'msg': error_msg,
				}
		else:
			# No existing record found, create new
			try:
				# Preserve original name from mbw_ats
				original_name = data.name
				
				# Create new document
				new_doc = frappe.new_doc("ATS_JobOpening")
				
				# IMPORTANT: Directly set the name to preserve the original ID
				new_doc.name = original_name
				
				# Set job opening fields
				job_fields = [
					"jo_id", "jo_public_title", "jo_internal_title", "jo_level_id", 
					"jo_profession_id", "jo_work_form", "jo_display_quantity",
					"jo_language_requirement", "publish_to_career_page", "jo_using_unit", 
					"jo_position", "jo_location", "jo_application_deadline", "status", 
					"applicants_applied", "jo_job_description", "jo_job_requirement", 
					"jo_job_benefits", "jo_contact_phone", "jo_contact_email",
					"jo_contact_person", "jo_currency", "jo_salary_display_option", 
					"jo_min_salary", "jo_max_salary"
				]
				
				# Set the sync ID and sync source flag
				new_doc.sync_id = original_name
				new_doc.sync_source = 1
				
				# Set other fields
				for field in job_fields:
					if hasattr(data, field) and getattr(data, field) is not None:
						setattr(new_doc, field, getattr(data, field))
				
				# Process recruitment_process child table - LƯU Ý tên bảng con chính xác là recruitment_process
				if hasattr(data, "recruitment_process") and isinstance(data.recruitment_process, list) and data.recruitment_process:
					frappe.logger("sync").debug(f"Adding {len(data.recruitment_process)} recruitment process records to new record")
					for round_data in data.recruitment_process:
						if isinstance(round_data, dict):
							new_doc.append("recruitment_process", {
								"round_name": round_data.get("round_name"),
								"round_type": round_data.get("round_type"),
								"position": round_data.get("position"),
								"default": round_data.get("default"),
								"test_link": round_data.get("test_link", ""),
								"automation_rules": round_data.get("automation_rules", "")
							})
				
				# Process hiring_committee child table
				if hasattr(data, "hiring_committee") and isinstance(data.hiring_committee, list) and data.hiring_committee:
					frappe.logger("sync").debug(f"Adding {len(data.hiring_committee)} hiring_committee members to new record")
					for member_data in data.hiring_committee:
						if isinstance(member_data, dict):
							new_doc.append("hiring_committee", {
								"user": member_data.get("user"),
								"notify_on_new_candidate": member_data.get("notify_on_new_candidate"),
								"can_view_offer_letter_details": member_data.get("can_view_offer_letter_details")
							})
				
				# Set flag to prevent triggering sync back and autoname
				new_doc.flags.ignore_sync = True
				# IMPORTANT: Prevent autoname from running
				new_doc.flags.name_set = True
				
				try:
					# Try to insert with our predefined name
					new_doc.insert(ignore_permissions=True)
					
					frappe.logger("sync").info(f"Created new job opening {new_doc.name} from sync operation, preserving original ID")
					
					return {
						'code': '00',
						'status': 'Success',
						'msg': 'Job opening created successfully with original ID',
						'job_opening_name': new_doc.name
					}
				except frappe.DuplicateEntryError as e:
					# If still encountering duplicate, log the error and return
					error_msg = f"Duplicate entry error for job opening with ID {original_name}: {str(e)}"
					frappe.logger("sync").error(error_msg)
					frappe.log_error(error_msg, "Sync Receive JobOpening Error")
					return {
						'code': '1',
						'status': 'Error',
						'msg': error_msg,
					}
				
			except Exception as e:
				error_msg = f"Failed to create new job opening: {str(e)}"
				frappe.logger("sync").error(error_msg)
				frappe.log_error(frappe.get_traceback(), error_msg)
				return {
					'code': '1',
					'status': 'Error',
					'msg': error_msg,
				}

	except Exception as e:
		error_msg = f"Sync receive job opening error: {str(e)}"
		frappe.logger("sync").error(error_msg)
		frappe.log_error(frappe.get_traceback(), error_msg)
		return {
			'code': '1',
			'status': 'Error',
			'msg': error_msg,
		}

"""########################### End Sync ATS_JobOpening ###########################"""