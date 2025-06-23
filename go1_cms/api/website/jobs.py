from mimetypes import guess_type
import frappe
import uuid
from frappe import _, local
from pypika import functions as fn
from go1_cms.api.common import (
    pretty_date,
    convert_str_to_list,
    send_email_manage,
    send_email_customer,
    get_domain
)
from go1_cms.api.website.log_page import (
    log_page_view
)
from dateutil import parser
from datetime import datetime
import math
from io import BytesIO
from captcha.image import ImageCaptcha
import string
import random
import base64
from frappe.utils import cint
from frappe.utils import now, add_to_date
import random
import string
import requests
import json
import os
from go1_cms.api.candidate_auth import send_password_setup_email

AI_BASEURL_V2 = frappe.conf.get("ai_baseurl_v2") or "http://n8n.fastwork.vn:8001"


@frappe.whitelist(allow_guest=True)
def get_filter_job():
    # job_type = frappe.db.get_all('CMS_JobOpening', fields=[
    #                              'employee_type_name as label', 'employee_type_name as value'], order_by='creation')
    job_type = []
    meta = frappe.get_meta('CMS_JobOpening')
    field = meta.get_field('jo_work_form')
    if field.options:
        if isinstance(field.options, str):
            options = field.options.split('\n')
        elif isinstance(field.options, list):
            options = field.options
        else:
            options = []
        job_type = [{
            "label" : item,
            "value" : item
        } for item in options]
        
    
    job_location = frappe.db.get_all(
        'ATS_Location', fields=['location_name as label', 'name as value'], order_by='creation asc')
    
    job_department = frappe.db.get_all(
        'ATS_Unit', fields=['unit_name as label', 'name as value'], order_by='creation asc')
    
    
    job_designation = frappe.db.get_all('ATS_Position', fields=[
        'position_name as label', 'name as value'], order_by='creation')

    return {
        'job_type': job_type,
        'job_location': job_location,
        'job_department': job_department,
        'job_designation': job_designation,
        'range_salary': {
            'from': 0,
            'to': 0
        }
    }


@frappe.whitelist(allow_guest=True)
def get_all_job(name_section, **kwargs):
    try:
        page_no = int(kwargs.get('page_no', 1)) - 1
        page_no = 0 if page_no < 1 else page_no
    except:
        page_no = 0

    page_len = 8
    text_search = kwargs.get('text_search', '')

    job_location = convert_str_to_list(kwargs.get('job_location', []))
    job_department = convert_str_to_list(kwargs.get('job_department', []))
    job_designation = convert_str_to_list(kwargs.get('job_designation', []))
    range_salary = convert_str_to_list(
        kwargs.get('range_salary', [None, None]))
    job_type = convert_str_to_list(kwargs.get('job_type', []))

    sort_by = frappe.qb.desc
    if kwargs.get('sort_by', 'desc').lower() == "asc":
        sort_by = frappe.qb.asc

    JobOpening = frappe.qb.DocType('CMS_JobOpening')
    
    # Debug: Check if doctype exists and has data
    if not frappe.db.exists("DocType", "CMS_JobOpening"):
        return {'data': [], 'pagination': {'current_page': 1, 'total': 0, 'total_page': 0, 'limit': page_len}, 'error': 'CMS_JobOpening doctype không tồn tại'}
    
    total_records = frappe.db.count('CMS_JobOpening')
    if total_records == 0:
        return {'data': [], 'pagination': {'current_page': 1, 'total': 0, 'total_page': 0, 'limit': page_len}, 'error': 'Không có dữ liệu trong CMS_JobOpening'}

    # Check Page Section exists
    if not frappe.db.exists("Page Section", name_section):
        # Use default values if section doesn't exist
        sort_field = 'jo_application_deadline'
        limit = page_len
    else:
        doc_section = frappe.get_doc('Page Section', name_section)
        sort_field = doc_section.sort_field if doc_section.sort_field else 'jo_application_deadline'
        limit = doc_section.no_of_records if doc_section.no_of_records else page_len
    
    # Validate sort_field exists in DocType
    meta = frappe.get_meta('CMS_JobOpening')
    valid_fields = [field.fieldname for field in meta.fields] + ['name', 'creation', 'modified']
    if sort_field not in valid_fields:
        sort_field = 'creation'  # Fallback to creation if sort_field is invalid
    
    offset = page_no * limit

    # Build base query
    m_query = frappe.qb.from_(JobOpening)
    
    # First, check if there are any published records
    published_count = frappe.db.count('CMS_JobOpening', {'publish_to_career_page': 1})
    if published_count == 0:
        # If no published records, return all records for debugging
        frappe.log_error("No published job openings found", "get_all_job_debug")
    else:
        # Only filter by published if there are published records
        m_query = m_query.where(JobOpening.publish_to_career_page == 1)
    
    # Apply filters
    if text_search:
        m_query = m_query.where(
            JobOpening.jo_public_title.like('%' + text_search+'%'))
    if job_location:
        m_query = m_query.where(JobOpening.jo_location.isin(job_location))
    if job_type:
        m_query = m_query.where(JobOpening.jo_work_form.isin(job_type))
    if job_department:
        m_query = m_query.where(JobOpening.jo_using_unit.isin(job_department))
    if job_designation:
        m_query = m_query.where(JobOpening.jo_position.isin(job_designation))

    if isinstance(range_salary, list):
        q = None
        salary_from = range_salary[0]
        salary_to = range_salary[1]

        if salary_from != None:
            salary_from = int(salary_from)
        if salary_to != None:
            salary_to = int(salary_to)

        if salary_from != None and salary_to == None:
            q = (JobOpening.jo_max_salary >= salary_from)
        elif salary_from == None and salary_to != None:
            q = (JobOpening.jo_min_salary <= salary_to)
        elif salary_from != None and salary_to != None:
            q = ((JobOpening.jo_min_salary <= salary_to) & (
                JobOpening.jo_max_salary >= salary_from))
        if q:
            m_query = m_query.where(q)
    
    # Build select query - fix duplicate jo_position field
    q_data = m_query.select(
        JobOpening.name, 
        JobOpening.jo_public_title, 
        JobOpening.jo_application_deadline,
        JobOpening.jo_location, 
        JobOpening.jo_work_form, 
        JobOpening.jo_min_salary, 
        JobOpening.route,
        JobOpening.jo_max_salary, 
        JobOpening.jo_position, 
        JobOpening.applicants_applied, 
        JobOpening.jo_currency
    ).offset(offset).limit(limit).orderby(JobOpening[sort_field], order=sort_by)

    jobs = q_data.run(as_dict=True)
    
    # Process date formatting
    for j in jobs:
        if j.jo_application_deadline:
            dt = datetime.combine(j.jo_application_deadline, datetime.min.time())
            j['pretty_posted_on'] = pretty_date(dt)
            j.jo_application_deadline = j.jo_application_deadline.strftime("%d-%m-%Y")

    # Count total results
    q_count = m_query.select(fn.Count('*').as_('total'))
    rs_count = q_count.run(as_dict=True)
    
    total = rs_count[0].total if rs_count and len(rs_count) > 0 else 0
    if limit > 0:
        total_page = math.ceil(total / limit)
    else:
        total_page = 0
        
    pagination = {
        'current_page': page_no + 1,
        'total': total,
        'total_page': total_page,
        'limit': limit,
    }
    
    # Add debug info
    debug_info = {
        'total_records_in_db': total_records,
        'published_records': published_count,
        'sort_field': sort_field,
        'query_result_count': len(jobs)
    }
    
    return {'data': jobs, 'pagination': pagination, 'debug': debug_info}


@frappe.whitelist(allow_guest=True)
def get_job_detail(name):
    if frappe.db.exists("CMS_JobOpening", name):
        doc = frappe.db.get_value('CMS_JobOpening', name, [
                                  'name', 'jo_public_title', 'jo_position', 'status', 'jo_application_deadline', 'jo_work_form', 'jo_using_unit', 'jo_location', 'jo_job_description', 'jo_currency', 'jo_min_salary', 'jo_max_salary', 'applicants_applied', 'route'], as_dict=1)
        return doc
    else:
        frappe.throw(_('Không tìm thấy công việc ứng tuyển'),
                     frappe.DoesNotExistError)


@frappe.whitelist(allow_guest=True)
def get_job_related(name, **kwargs):
    jobs = []
    if frappe.db.exists("CMS_JobOpening", name):
        doc = frappe.db.get_value('CMS_JobOpening', name, [
            'name', 'jo_public_title', 'jo_position', 'status', 'jo_work_form', 'jo_location'], as_dict=1)

        name_section = kwargs.get('name_section', None)
        if name_section:
            doc_section = frappe.db.get_value('Page Section', name_section, [
                                              'no_of_records'], as_dict=1)
            limit = doc_section.no_of_records if doc_section.no_of_records else 4
        else:
            limit = kwargs.get('limit', '4')
            if limit.isdigit():
                limit = int(limit) if int(limit) <= 12 else 12
            else:
                limit = 4

        JobOpening = frappe.qb.DocType('CMS_JobOpening')
        m_query = (frappe.qb.from_(JobOpening).where(
            (JobOpening.name != name) & (JobOpening.publish_to_career_page == 1)))
        q = None

        if doc.jo_location:
            q = (q | (JobOpening.jo_location == doc.jo_location)) if q else (
                JobOpening.jo_location == doc.jo_location)
        if doc.jo_position:
            q = (q | (JobOpening.jo_position == doc.jo_position)) if q else (
                JobOpening.jo_position == doc.jo_position)
        if doc.jo_work_form:
            q = (q | (JobOpening.jo_work_form == doc.jo_work_form)) if q else (
                JobOpening.jo_work_form == doc.jo_work_form)
        if doc.jo_public_title:
            q = (q | (JobOpening.jo_public_title.like('%' + doc.jo_public_title+'%'))) if q else (
                JobOpening.jo_public_title.like('%' + doc.jo_public_title+'%'))

        if q:
            m_query = m_query.where(q)
        q_data = m_query.select(JobOpening.name, JobOpening.jo_public_title, JobOpening.jo_application_deadline,
                                JobOpening.jo_location, JobOpening.jo_work_form, JobOpening.jo_min_salary, JobOpening.route,
                                JobOpening.jo_max_salary, JobOpening.jo_using_unit, JobOpening.applicants_applied, JobOpening.jo_position, JobOpening.jo_currency
                                ).limit(limit).orderby(JobOpening.jo_application_deadline, order=frappe.qb.desc)

        jobs = q_data.run(as_dict=True)
        for j in jobs:
            if j.jo_application_deadline:
                dt = datetime.combine(j.jo_application_deadline, datetime.min.time())
                j['pretty_posted_on'] = pretty_date(dt)
                j.jo_application_deadline = j.jo_application_deadline.strftime("%d-%m-%Y")

    return {"jobs": jobs}


@frappe.whitelist(methods=['POST'], allow_guest=True)
def upload_cv(name_job, **kwargs):
    """
    API gốc để upload CV (tương thích ngược)
    """
    try:
        applicant_name = kwargs.get('full_name', None)
        email = kwargs.get('email', None)
        phone_number = kwargs.get('phone_number', None)
        files = frappe.request.files
        captcha_text = kwargs.get('captcha_text', None)
        form_name = kwargs.get('form_name', None)
        ip = local.request.remote_addr

        if not form_name or not frappe.db.exists("MBW Form", form_name):
            frappe.throw('Mã biểu mẫu không đúng')

        captcha = frappe.db.get_value('CMS Captcha', {
            "ip": ip, 'captcha_text': captcha_text.strip().upper()}, ['name', 'creation'], as_dict=1)
        if not captcha_text or not captcha:
            return {
                'status': '0',
                'msg': 'Mã captcha không đúng'
            }

        old_datetime = datetime.strptime(
            add_to_date(now(), minutes=-10), "%Y-%m-%d %H:%M:%S.%f")
        if old_datetime >= captcha.creation:
            return {
                'status': '1',
                'msg': 'Mã captcha đã hết hạn'
            }

        if not applicant_name:
            frappe.throw('Họ tên không được để trống')
        if not email:
            frappe.throw('Email không được để trống')
        
        if not phone_number:
            frappe.throw('Số điện thoại không được để trống')

        # Find job opening in both CMS_JobOpening and ATS_JobOpening
        from go1_cms.api.fix_job_doctype import find_job_opening
        job_info = find_job_opening(name_job)
        
        if job_info["found"]:
            job_data = job_info["data"]
            jo_public_title = job_info["job_title"]
            if frappe.db.exists('ATS_Candidate', {'can_email': email, 'job_opening_id': jo_public_title}):
                frappe.throw('Bạn đã ứng tuyển vị trí này từ trước')
            new_doc = frappe.new_doc('ATS_Candidate')
            new_doc.can_id = generate_random_id()
            new_doc.can_full_name = applicant_name
            new_doc.can_email = email
            new_doc.can_phone = phone_number
            new_doc.job_opening_id = jo_public_title
            new_doc.sync_id = str(uuid.uuid4())
            new_doc.candidatesource_id = "Website"  # Set candidate source
            # Allow webhook sync for candidate sync to ATS
            frappe.flags.ignore_webhook_sync = False
            doc_saved = new_doc.save(ignore_permissions=True)
            frappe.db.commit()
            filename = ''
            new_file=None

            if 'file_cv' in files:
                file_cv = files["file_cv"]
                content = file_cv.stream.read()
                filename = file_cv.filename
                ct = datetime.now()

                file_cv.seek(0, 2)
                size = file_cv.tell()
                file_cv.seek(0)

                str_ts = str(math.floor(ct.timestamp()))
                sp_fn = filename.split('.')
                if len(sp_fn) == 2:
                    filename = sp_fn[0] + '_' + str_ts + '.' + sp_fn[1]

                content_type = guess_type(filename)[0]
                if content_type != "application/pdf":
                    frappe.throw('Tên tệp không đúng định dạng')

                form_fields = frappe.db.get_all("MBW Form Item", filters={"parent": form_name, "parentfield": "form_fields", "field_name": "file_cv"}, fields=[
                    'max_file_size'
                ])
                if not form_fields or form_fields[0].max_file_size*1024**2 < size:
                    frappe.throw(
                        f'Tệp không vượt quá {form_fields[0].max_file_size}MB')

                new_file = frappe.get_doc(
                    {
                        "doctype": "File",
                        "attached_to_doctype": "ATS_Candidate",
                        "attached_to_name": doc_saved.name,
                        "attached_to_field": "can_cv",
                        "folder": "Home",
                        "file_name": filename,
                        "file_url": "",
                        "is_private": 0,
                        "content": content,
                    }
                )
                new_file.save(ignore_permissions=True)

            if new_file:
                can_doc = frappe.get_doc("ATS_Candidate",doc_saved.name)
                can_doc.can_cv = new_file.file_url
                can_doc.save(ignore_permissions=True)
                frappe.db.commit()
            
            ### send email ###
            domain = get_domain()
            redirect_to = f'{domain}/app/job-applicant/{new_doc.name}'
            args = {
                'time': format_creation(new_doc.creation),
                'job_title': jo_public_title,
                'designation': job_data.jo_position,
                'location': job_data.jo_location,
                'employment_type': job_data.jo_work_form,
                'department': job_data.jo_using_unit,
                'lower_range': job_data.jo_min_salary,
                'upper_range': job_data.jo_max_salary,
                'currency': job_data.jo_currency,
                'salary_per': 'Tháng',
                'full_name': applicant_name,
                'email': email,
                'phone_number': phone_number,
                'redirect_to': redirect_to,
            }
            send_email_manage(None, 'email_apply_cv_manage', args)

            # Send password setup email for candidate
            try:
                from go1_cms.api.candidate_auth import send_password_setup_email
                setup_result = send_password_setup_email(email)
                if setup_result.get("success"):
                    frappe.logger().info(f"Password setup email sent successfully to {email}")
                else:
                    frappe.logger().error(f"Failed to send password setup email to {email}: {setup_result.get('message')}")
            except Exception as email_error:
                frappe.log_error(frappe.get_traceback(), "Send Password Setup Email Error")
                frappe.logger().error(f"Error sending password setup email to {email}: {str(email_error)}")

            frappe.enqueue(log_page_view, queue='default', ip=ip,
                        form_type="Recruitment form")
            # delete captcha
            frappe.db.delete("CMS Captcha", {'name': captcha.name})

            return {'status': '200', 'name': doc_saved.name}
        else:
            frappe.throw(_('Không tìm thấy công việc ứng tuyển'))
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except Exception as ex:
        frappe.throw(_("Upload không thành công. Vui lòng thử lại!"))

def format_creation(creation):
    if isinstance(creation, str):
        try:
            creation = datetime.strptime(creation, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            creation = datetime.strptime(creation, "%Y-%m-%d %H:%M:%S")
    return creation.strftime("%d/%m/%Y %H:%M:%S")

def generate_random_id(length=16):
    characters = string.ascii_uppercase + string.digits
    while True:
        random_id = ''.join(random.choices(characters, k=length))
        # Kiểm tra xem mã đã tồn tại trong ATS_Candidate chưa
        if not frappe.db.exists('ATS_Candidate', {'can_id': random_id}):
            return random_id

@frappe.whitelist(allow_guest=True)
def get_info_candidate():
	return {
		"data": {
			"can_full_name": "Trần Mạnh Mẽ",
			"can_dob": "10/04/1999",
			"can_phone": "09281818282",
			"can_address": "Ba Đình, Hà Nội",
			"can_avatar": "avar.png",
			"recruitment_process": [
				{
					"label": "Phỏng vấn vòng 1",
					"status": "done",
					"detail": {
						"status": "Đã hoàn thành",
						"interviewer": "Chu Quỳnh Anh, Phạm Thị Hạnh",
						"time": "Thứ 3, ngày 06 tháng 05 năm 2025, 10:00 - 11:30",
					},
				},
				{
					"label": "Phỏng vấn vòng 2",
					"status": "active",
					"detail": {
						"status": "Đang thực hiện",
						"interviewer": "Chu Quỳnh Anh, Phạm Thị Hạnh",
						"time": "Thứ 3, ngày 13 tháng 05 năm 2025, 10:00 - 11:30",
					},
				},
				{
					"label": "Làm bài test",
					"status": "pending",
					"detail": {
						"status": "Chưa thực hiện",
						"interviewer": "-",
						"time": "-",
					},
				},
			]
		}
	}

def generate_random_id(length=16):
    characters = string.ascii_uppercase + string.digits
    while True:
        random_id = ''.join(random.choices(characters, k=length))
        # Kiểm tra xem mã đã tồn tại trong ATS_Candidate chưa
        if not frappe.db.exists('ATS_Candidate', {'can_id': random_id}):
            return random_id

@frappe.whitelist(methods=['POST'], allow_guest=True)
def upload_file_only():
    """
    API để chỉ upload file CV lên server, trả về file_name để dùng cho AI extraction
    """
    try:
        files = frappe.request.files
        
        if 'file_cv' not in files:
            frappe.throw('Không tìm thấy file CV')
            
        file_cv = files["file_cv"]
        content = file_cv.stream.read()
        filename = file_cv.filename
        ct = datetime.now()

        file_cv.seek(0, 2)
        size = file_cv.tell()
        file_cv.seek(0)

        # Validate file
        content_type = guess_type(filename)[0]
        if content_type != "application/pdf":
            frappe.throw('Chỉ chấp nhận file PDF')

        if size > 10 * 1024 * 1024:  # 10MB limit
            frappe.throw('File không được vượt quá 10MB')

        # Generate unique filename
        str_ts = str(math.floor(ct.timestamp()))
        sp_fn = filename.split('.')
        if len(sp_fn) == 2:
            filename = sp_fn[0] + '_' + str_ts + '.' + sp_fn[1]

        # Create temporary file document
        new_file = frappe.get_doc({
            "doctype": "File",
            "folder": "Home",
            "file_name": filename,
            "file_url": "",
            "is_private": 0,
            "content": content,
        })
        new_file.save(ignore_permissions=True)

        return {
            'status': 'success',
            'file_name': new_file.name,
            'file_url': new_file.file_url,
            'original_filename': file_cv.filename,
            'size': size
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Upload File Only Error")
        return {'status': 'error', 'message': str(e)}


@frappe.whitelist()
def extract_cv_url():
    """
    API để extract thông tin CV bằng AI từ file đã upload
    """
    AI_BASEURL = frappe.conf.get("ai_baseurl") or "https://taskingai.mbwcloud.com"
    url_extract_ai = f"{AI_BASEURL_V2}/api/v1/cv_extract"
    
    file_name = frappe.form_dict.get("file_name")
    if not file_name:
        frappe.throw("Missing 'file_name' in request parameters.")

    headers = {
        "x-api-key":"6Bwunlw3Fm1J23tGKZjb/WJXwBDI3gRY971+VUFOU+w="
    }

    try:
        file_doc = frappe.db.get_value(
            "File", {"name": file_name}, ["file_name", "file_url"], as_dict=1
        )
        if not file_doc:
            return {"error": "File not found", "file_name": file_name}
        
        # Use the correct file path - check both possibilities
        file_path = None
        
        # Try site path first (relative to site)
        relative_file_path = file_doc.file_url.lstrip("/")
        full_file_path = frappe.utils.get_site_path("public", relative_file_path)
        
        if os.path.exists(full_file_path):
            file_path = full_file_path
        else:
            # Try legacy path
            legacy_path = frappe.utils.get_files_path(file_doc.file_name)
            if os.path.exists(legacy_path):
                file_path = legacy_path
            else:
                return {"error": f"File not found at expected paths: {full_file_path}, {legacy_path}"}

        with open(file_path, "rb") as f:
            files = {"file": (file_doc.file_name, f, "application/pdf")}
            response = requests.post(url_extract_ai, files=files, headers=headers)

        if response.status_code == 200:
            data = frappe.parse_json(response.json())
            if data and data.data:
                if "personal_info" in data.data:
                    personal_info = {
                        "name": "can_full_name",
                        "email": "can_email", 
                        "phone": "can_phone",
                    }
                    data.data["personal_info"] = rename_keys(
                        data.data["personal_info"], personal_info
                    )

                if "work_experience" in data.data:
                    work_experience = {
                        "company": "work_experience_place",
                        "position": "work_experience_role",
                        "start_date": "work_experience_start",
                        "end_date": "work_experience_end",
                        "descriptions": "work_experience_detail",
                    }
                    data.data["work_experience"] = rename_keys_in_list(
                        data.data["work_experience"], work_experience
                    )

                if "projects" in data.data:
                    projects = {
                        "name": "projects_name",
                        "tasks": "project_description",
                        "start_date": "project_start_date",
                        "end_date": "project_end_date",
                        "position": "project_role",
                    }
                    data.data["projects"] = rename_keys_in_list(
                        data.data["projects"], projects
                    )

                if "skills" in data.data:
                    skill = {
                        "name": "can_skill_name",
                    }
                    data.data["skills"] = rename_keys_in_list(
                        data.data["skills"], skill
                    )

                # Xử lý ảnh avatar nếu có
                if "list_imgs_base64" in data and data["list_imgs_base64"]:
                    try:
                        data.data["can_avatar"] = upload_base64_without_filename(
                            data["list_imgs_base64"][0],
                            "ATS_Candidate",
                            data.data["personal_info"].get("can_full_name", "unknown"),
                        )
                    except Exception as avatar_error:
                        frappe.log_error(str(avatar_error), "CV Avatar Upload Error")
                        data.data["can_avatar"] = None
                    finally:
                        del data["list_imgs_base64"]
                else:
                    data.data["can_avatar"] = None

            return data
        else:
            frappe.log_error(
                f"CV Upload API Error {response.status_code}: {response.text}",
                "CV Upload API",
            )
            return {
                "error": "CV extraction failed",
                "status_code": response.status_code,
                "response": response.text,
            }

    except frappe.DoesNotExistError:
        return {"error": "File not found", "file_name": file_name}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "CV Upload API")
        return {
            "error": "Unhandled error occurred while processing the CV.",
            "details": str(e),
        }


def rename_keys(data, rename_map):
    """Helper function to rename keys in dictionary"""
    return {rename_map.get(k, k): v for k, v in data.items()}


def rename_keys_in_list(data_list, rename_map):
    """Helper function to rename keys in list of dictionaries"""
    return [{rename_map.get(k, k): v for k, v in item.items()} for item in data_list]


def upload_base64_without_filename(base64_string, doctype, docname):
    """Helper function to upload base64 image"""
    try:
        import base64
        from io import BytesIO
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Create file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"avatar_{docname}.jpg",
            "content": image_data,
            "is_private": 0,
        })
        file_doc.save(ignore_permissions=True)
        
        return file_doc.file_url
    except Exception as e:
        frappe.log_error(str(e), "Upload Base64 Avatar Error")
        return None
def try_parse_date(value):
    if isinstance(value, str):
        try:
            dt = parser.parse(value, dayfirst=True)
            return dt.strftime('%Y-%m-%d')
        except:
            return value
    return value

def normalize_dates_recursively(obj):
    if isinstance(obj, dict):
        for key in obj:
            obj[key] = normalize_dates_recursively(obj[key])
        return obj
    elif isinstance(obj, list):
        return [normalize_dates_recursively(item) for item in obj]
    else:
        return try_parse_date(obj)

def map_ai_data_to_doctype_format(data):
    """
    Map AI extracted data to DocType field format
    """
    mapped_data = {}
    
    # Map projects data
    if data.get("projects"):
        mapped_projects = []
        for project in data["projects"]:
            mapped_project = {
                "project_name": project.get("projects_name", ""),
                "project_role": project.get("project_role", ""),
                "project_description": project.get("project_description", ""),
                "project_start_date": project.get("project_start_date", ""),
                "project_end_date": project.get("project_end_date", "")
            }
            mapped_projects.append(mapped_project)
        mapped_data["projects"] = mapped_projects
    
    # Work experience should already be in correct format based on the rename_keys function
    if data.get("work_experience"):
        mapped_data["work_experience"] = data["work_experience"]
    
    # Skills should already be in correct format
    if data.get("skills"):
        mapped_data["skills"] = data["skills"]
    
    # Certificates - map from 'certificate' to correct format
    if data.get("certificate"):
        mapped_certs = []
        for cert in data["certificate"]:
            mapped_cert = {
                "can_cert_name": cert.get("name", ""),
                "can_cert_organization": cert.get("organization", ""),
                "can_cert_issued_date": cert.get("start_date", ""),
                "can_cert_expiration_date": cert.get("end_date", ""),
                "can_cert_link": ""  # No link in AI data
            }
            mapped_certs.append(mapped_cert)
        mapped_data["certificates"] = mapped_certs
    
    # Awards
    if data.get("awards"):
        mapped_awards = []
        for award in data["awards"]:
            mapped_award = {
                "can_award_name": award.get("name", ""),
                "can_award_organization": award.get("organization", ""),
                "can_award_received_date": award.get("end_date", ""),
                "can_award_link": ""  # No link in AI data
            }
            mapped_awards.append(mapped_award)
        mapped_data["awards"] = mapped_awards
    
    # Copy other data as is
    for key in ["personal_info", "can_avatar", "list_imgs_base64"]:
        if data.get(key):
            mapped_data[key] = data[key]
    
    return mapped_data
@frappe.whitelist(methods=['POST'], allow_guest=True)
def upload_cv_with_ai_extraction(name_job, **kwargs):
    """
    API để submit form với dữ liệu đã được AI extract
    File đã được upload trước đó qua upload_file_only()
    """
    try:
        applicant_name = kwargs.get('full_name', None)
        email = kwargs.get('email', None)
        phone_number = kwargs.get('phone_number', None)
        captcha_text = kwargs.get('captcha_text', None)
        form_name = kwargs.get('form_name', None)
        file_name = kwargs.get('file_name', None)  # File đã upload trước đó
        ip = local.request.remote_addr

        if not form_name or not frappe.db.exists("MBW Form", form_name):
            frappe.throw('Mã biểu mẫu không đúng')

        # Validate captcha
        captcha = frappe.db.get_value('CMS Captcha', {
            "ip": ip, 'captcha_text': captcha_text.strip().upper()}, ['name', 'creation'], as_dict=1)
        if not captcha_text or not captcha:
            return {
                'status': '0',
                'msg': 'Mã captcha không đúng'
            }

        old_datetime = datetime.strptime(
            add_to_date(now(), minutes=-10), "%Y-%m-%d %H:%M:%S.%f")
        if old_datetime >= captcha.creation:
            return {
                'status': '1',
                'msg': 'Mã captcha đã hết hạn'
            }

        # Basic validation
        if not applicant_name:
            frappe.throw('Họ tên không được để trống')
        if not email:
            frappe.throw('Email không được để trống')
        if frappe.db.exists('ATS_Candidate', {'can_email': email, 'job_opening_id': name_job}):
            frappe.throw('Bạn đã ứng tuyển vị trí này từ trước')
        if not phone_number:
            frappe.throw('Số điện thoại không được để trống')

        # Find job opening in both CMS_JobOpening and ATS_JobOpening
        from go1_cms.api.fix_job_doctype import find_job_opening
        job_info = find_job_opening(name_job)
        
        if job_info["found"]:
            job_data = job_info["data"]
            jo_public_title = job_info["job_title"]
            if frappe.db.exists('ATS_Candidate', {'can_email': email, 'job_opening_id': jo_public_title}):
                frappe.throw('Bạn đã ứng tuyển vị trí này từ trước')
            # Create new candidate
            new_doc = frappe.new_doc('ATS_Candidate')
            new_doc.can_id = generate_random_id()
            new_doc.can_full_name = applicant_name
            new_doc.can_email = email
            new_doc.can_phone = phone_number
            new_doc.job_opening_id = jo_public_title  # Use title instead of name_job for consistency
            new_doc.sync_id = str(uuid.uuid4())  # Add sync_id for ATS sync
            new_doc.candidatesource_id = "Website"  # Set candidate source
            
            # Allow webhook sync for candidate sync to ATS
            frappe.flags.ignore_webhook_sync = False
            
            # Handle extracted data from AI
            extracted_data_raw = kwargs.get('extracted_data')
            print("Received extracted_data_raw:", extracted_data_raw)

            if extracted_data_raw:
                try:
                    extracted_data = json.loads(extracted_data_raw) if isinstance(extracted_data_raw, str) else extracted_data_raw
                    print("Parsed extracted_data:", extracted_data)
                    
                    # Extract the actual data from the payload
                    data = extracted_data.get("data", {})
                    print("Data section:", data)
                    
                    # Normalize dates in the data
                    data = normalize_dates_recursively(data)
                    
                    # Map AI data to DocType format
                    mapped_data = map_ai_data_to_doctype_format(data)
                    print("Mapped data:", mapped_data)
                    
                    # Handle personal info
                    personal_info = mapped_data.get("personal_info", {})
                    if personal_info:
                        print("Processing personal_info:", personal_info)
                        if personal_info.get("can_full_name") and len(personal_info["can_full_name"]) > len(applicant_name):
                            new_doc.can_full_name = personal_info["can_full_name"]
                        if personal_info.get("can_phone"):
                            new_doc.can_phone = personal_info["can_phone"]
                        if personal_info.get("dob"):
                            new_doc.can_dob = personal_info.get("dob", "")

                    # Handle avatar
                    if mapped_data.get("can_avatar"):
                        new_doc.can_avatar = mapped_data["can_avatar"]

                    # Handle work experience
                    work_experience = mapped_data.get("work_experience", [])
                    if work_experience:
                        print("Processing work_experience:", len(work_experience), "items")
                        for we in work_experience:
                            new_doc.append("candidate_work_experience", we)

                    # Handle projects
                    projects = mapped_data.get("projects", [])
                    if projects:
                        print("Processing projects:", len(projects), "items")
                        for project in projects:
                            new_doc.append("candidate_project", project)

                    # Handle skills
                    skills = mapped_data.get("skills", [])
                    if skills:
                        print("Processing skills:", len(skills), "items")
                        for skill in skills:
                            new_doc.append("candidate_skill", skill)

                    # Handle certificates (correct field name is candidate_certification)
                    certificates = mapped_data.get("certificates", [])
                    if certificates:
                        print("Processing certificates:", len(certificates), "items")
                        for cert in certificates:
                            new_doc.append("candidate_certification", cert)

                    # Handle awards
                    awards = mapped_data.get("awards", [])
                    if awards:
                        print("Processing awards:", len(awards), "items")
                        for award in awards:
                            new_doc.append("candidate_award", award)

                    # Handle base64 images if available
                    if mapped_data.get("list_imgs_base64"):
                        try:
                            new_doc.can_avatar = upload_base64_without_filename(
                                mapped_data["list_imgs_base64"][0],
                                "ATS_Candidate",
                                new_doc.can_full_name,
                            )
                        except Exception as avatar_error:
                            frappe.log_error(str(avatar_error), "CV Avatar Upload Error")
                            new_doc.can_avatar = None
                    elif not mapped_data.get("can_avatar"):
                        new_doc.can_avatar = None

                except Exception as data_error:
                    frappe.log_error(frappe.get_traceback(), "Process Extracted Data Error")
                    print("Error processing extracted data:", str(data_error))

            # Save candidate first to get the name
            new_doc.save(ignore_permissions=True)
            frappe.db.commit()
            new_doc.reload()

            # Attach uploaded file to candidate if file_name provided
            if file_name and frappe.db.exists("File", file_name):
                file_doc = frappe.get_doc("File", file_name)
                file_doc.attached_to_doctype = "ATS_Candidate"
                file_doc.attached_to_name = new_doc.name
                file_doc.attached_to_field = "can_cv"
                file_doc.save(ignore_permissions=True)
                new_doc.can_cv = file_doc.file_url
                new_doc.save(ignore_permissions=True)

            # Send email notification
            domain = get_domain()
            redirect_to = f'{domain}/app/job-applicant/{new_doc.name}'
            args = {
                'time': new_doc.creation.strftime("%d/%m/%Y %H:%M:%S"),
                'job_title': jo_public_title,
                'designation': job_data.jo_position,
                'location': job_data.jo_location,
                'employment_type': job_data.jo_work_form,
                'department': job_data.jo_using_unit,
                'lower_range': job_data.jo_min_salary,
                'upper_range': job_data.jo_max_salary,
                'currency': job_data.jo_currency,
                'salary_per': 'Tháng',
                'full_name': new_doc.can_full_name,
                'email': email,
                'phone_number': phone_number,
                'redirect_to': redirect_to,
            }
            send_email_manage(None, 'email_apply_cv_manage', args)

            # Send password setup email for candidate
            try:
                from go1_cms.api.candidate_auth import send_password_setup_email
                setup_result = send_password_setup_email(email)
                if setup_result.get("success"):
                    frappe.logger().info(f"Password setup email sent successfully to {email}")
                else:
                    frappe.logger().error(f"Failed to send password setup email to {email}: {setup_result.get('message')}")
            except Exception as email_error:
                frappe.log_error(frappe.get_traceback(), "Send Password Setup Email Error")
                frappe.logger().error(f"Error sending password setup email to {email}: {str(email_error)}")

            frappe.enqueue(log_page_view, queue='default', ip=ip, form_type="Recruitment form")
            # Delete captcha
            frappe.db.delete("CMS Captcha", {'name': captcha.name})

            return {
                'status': '200', 
                'name': new_doc.name,
                'candidate_data': new_doc.as_dict()
            }
        else:
            frappe.throw(_('Không tìm thấy công việc ứng tuyển'))
            
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except Exception as ex:
        frappe.log_error(frappe.get_traceback(), "Upload CV With AI Extraction Error")
        frappe.throw(_("Upload không thành công. Vui lòng thử lại!"), ex)


@frappe.whitelist(allow_guest=True)
def get_recruitment_form_template_data(form_name, enable_ai=False):
    """
    API để lấy template data cho recruitment form với option AI extraction
    """
    try:
        if not form_name or not frappe.db.exists("MBW Form", form_name):
            frappe.throw('Form không tồn tại')
            
        form_doc = frappe.get_doc("MBW Form", form_name)
        form_fields = frappe.get_all("MBW Form Item", 
                                    filters={"parent": form_name, "parentfield": "form_fields"}, 
                                    fields=["*"], 
                                    order_by="idx")
        
        return {
            "form_data": form_doc.as_dict(),
            "form_fields": form_fields,
            "ai_extraction_enabled": enable_ai,
            "api_endpoint": "upload_cv_with_ai_extraction" if enable_ai else "upload_cv"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Recruitment Form Template Error")
        return {"error": str(e)}


