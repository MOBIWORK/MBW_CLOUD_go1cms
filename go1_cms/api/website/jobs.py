from mimetypes import guess_type
import frappe
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
from datetime import datetime
import math
from io import BytesIO
from captcha.image import ImageCaptcha
import string
import random
import base64
from frappe.utils import cint
from frappe.utils import now, add_to_date


@frappe.whitelist(allow_guest=True)
def get_filter_job():
    # job_type = frappe.db.get_all('ATS_JobOpening', fields=[
    #                              'employee_type_name as label', 'employee_type_name as value'], order_by='creation')
    job_type = []
    meta = frappe.get_meta('ATS_JobOpening')
    field = meta.get_field('jo_work_form')
    if field.options:
        options = field.options.split('\n')
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

    JobOpening = frappe.qb.DocType('ATS_JobOpening')

    doc_section = frappe.get_doc('Page Section', name_section)
    sort_field = doc_section.sort_field if doc_section.sort_field else 'jo_application_deadline'
    limit = doc_section.no_of_records if doc_section.no_of_records else page_len
    offset = page_no*limit

    # get data
    m_query = (frappe.qb.from_(JobOpening))
    if text_search:
        m_query = m_query.where(
            JobOpening.job_title.like('%' + text_search+'%'))
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
    q_data = m_query.select(JobOpening.name, JobOpening.jo_public_title, JobOpening.jo_application_deadline,
                            JobOpening.jo_location, JobOpening.jo_work_form, JobOpening.jo_min_salary,
                            JobOpening.jo_max_salary, JobOpening.jo_position, JobOpening.applicants_applied, JobOpening.jo_position, JobOpening.jo_currency
                            ).offset(offset).limit(limit).orderby(JobOpening[sort_field], order=sort_by)

    jobs = q_data.run(as_dict=True)

    

    for j in jobs:
        dt = datetime.combine(j.jo_application_deadline, datetime.min.time())
        j['pretty_posted_on'] = pretty_date(dt)

    q_count = m_query.select(fn.Count('*').as_('total'))
    rs_count = q_count.run(as_dict=True)
    if rs_count and limit > 0:
        total_page = math.ceil(rs_count[0].total/limit)
    else:
        total_page = 0
    pagination = {
        'current_page': page_no + 1,
        'total': rs_count[0].total if rs_count and limit > 0 else 0,
        'total_page': total_page,
        'limit': limit,
    }
    return {'data': jobs, 'pagination': pagination}


@frappe.whitelist(allow_guest=True)
def get_job_detail(name):
    if frappe.db.exists("ATS_JobOpening", name):
        doc = frappe.db.get_value('ATS_JobOpening', name, [
                                  'name', 'jo_public_title', 'jo_position', 'status', 'jo_application_deadline', 'jo_work_form', 'jo_using_unit', 'jo_location', 'jo_job_description', 'jo_currency', 'jo_min_salary', 'jo_max_salary', 'applicants_applied'], as_dict=1)
        return doc
    else:
        frappe.throw(_('Không tìm thấy công việc ứng tuyển'),
                     frappe.DoesNotExistError)


@frappe.whitelist(allow_guest=True)
def get_job_related(name, **kwargs):
    jobs = []
    if frappe.db.exists("ATS_JobOpening", name):
        doc = frappe.db.get_value('ATS_JobOpening', name, [
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

        JobOpening = frappe.qb.DocType('ATS_JobOpening')
        m_query = (frappe.qb.from_(JobOpening).where(
            (JobOpening.name != name)))
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
                                JobOpening.jo_location, JobOpening.jo_work_form, JobOpening.jo_min_salary,
                                JobOpening.jo_max_salary, JobOpening.jo_using_unit, JobOpening.applicants_applied, JobOpening.jo_position, JobOpening.jo_currency
                                ).limit(limit).orderby(JobOpening.jo_application_deadline, order=frappe.qb.desc)

        jobs = q_data.run(as_dict=True)
        for j in jobs:
            dt = datetime.combine(j.jo_application_deadline, datetime.min.time())
            j['pretty_posted_on'] = pretty_date(dt)

    return {"jobs": jobs}


@frappe.whitelist(methods=['POST'], allow_guest=True)
def upload_cv(name_job, **kwargs):
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
        "ip": ip, 'captcha_text': captcha_text}, ['name', 'creation'], as_dict=1)
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

    if frappe.db.exists("ATS_JobOpening", name_job):
        new_doc = frappe.new_doc('ATS_Candidate')
        new_doc.can_full_name = applicant_name
        new_doc.can_email = email
        new_doc.can_phone = phone_number
        new_doc.job_opening_id = name_job
        new_doc.save(ignore_permissions=True)
        new_doc.reload()

        filename = ''
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
                    "attached_to_doctype": "Job Applicant",
                    "attached_to_name": new_doc.name,
                    "attached_to_field": "resume_attachment",
                    "folder": "Home",
                    "file_name": filename,
                    "file_url": "",
                    "is_private": 0,
                    "content": content,
                }
            )
            new_file.save(ignore_permissions=True)
            new_doc.resume_attachment = new_file.file_url

        new_doc.save(ignore_permissions=True)

        ### send email ###
        domain = get_domain()
        redirect_to = f'{domain}/app/job-applicant/{new_doc.name}'
        job_open = frappe.db.get_value(
            'ATS_JobOpening', name_job,
            ['jo_public_title', 'jo_work_form', 'jo_location',
                'jo_using_unit', 'jo_position', 'jo_min_salary', 'jo_max_salary', 'jo_currency'],
            as_dict=1
        )
        args = {
            'time': new_doc.creation.strftime("%d/%m/%Y %H:%M:%S"),
            'job_title': job_open.jo_public_title,
            'designation': job_open.jo_position,
            'location': job_open.jo_location,
            'employment_type': job_open.jo_work_form,
            'department': job_open.jo_using_unit,
            'lower_range': job_open.jo_min_salary,
            'upper_range': job_open.jo_max_salary,
            'currency': job_open.jo_currency,
            'salary_per': 'Tháng',
            'full_name': applicant_name,
            'email': email,
            'phone_number': phone_number,
            'redirect_to': redirect_to,
        }
        send_email_manage(None, 'email_apply_cv_manage', args)

        frappe.enqueue(log_page_view, queue='default', ip=ip,
                       form_type="Recruitment form")
        # delete captcha
        frappe.db.delete("CMS Captcha", {'name': captcha.name})

        return {'status': '200', 'name': new_doc.name}
    else:
        frappe.throw(_('Không tìm thấy công việc ứng tuyển'),
                     frappe.DoesNotExistError)
