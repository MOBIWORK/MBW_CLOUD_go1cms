#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def check_candidate_status(full_name, email):
    """
    Check candidate status across different job applications
    
    Args:
        full_name (str): Candidate's full name
        email (str): Candidate's email address
    
    Returns:
        dict: Candidate information and application status
    """
    
    try:
        if not full_name or not email:
            return {
                'success': False,
                'message': _("Vui lòng nhập đầy đủ họ tên và email"),
                'data': []
            }
        
        # Tìm candidates có cùng email hoặc tên (có thể có nhiều ATS_Candidate khác nhau)
        candidates = frappe.db.sql("""
            SELECT 
                c.name as candidate_id,
                c.can_id,
                c.can_full_name,
                c.can_email,
                c.can_phone,
                c.can_avatar,
                c.job_opening_id,
                c.status,
                c.can_application_date,
                c.can_recruiter,
                c.candidatesource_id,
                j.jo_public_title,
                j.jo_internal_title,
                j.jo_position,
                j.jo_location,
                j.status as job_status,
                j.jo_application_deadline,
                j.route as job_route
            FROM `tabATS_Candidate` c
            LEFT JOIN `tabATS_JobOpening` j ON c.job_opening_id = j.name
            WHERE 
                (LOWER(c.can_email) = %(email)s OR LOWER(c.can_full_name) = %(full_name)s)
                AND c.docstatus != 2
            ORDER BY c.can_application_date DESC
        """, {
            'email': email.lower(),
            'full_name': full_name.lower()
        }, as_dict=True)
        
        if not candidates:
            return {
                'success': False,
                'message': _("Không tìm thấy thông tin ứng viên với tên và email này"),
                'data': []
            }
        
        # Nhóm theo candidate để xử lý trường hợp có nhiều ATS_Candidate cùng email/tên
        candidate_groups = {}
        
        for candidate in candidates:
            key = f"{candidate.can_full_name}_{candidate.can_email}"
            
            if key not in candidate_groups:
                candidate_groups[key] = {
                    'candidate_info': {
                        'full_name': candidate.can_full_name,
                        'email': candidate.can_email,
                        'phone': candidate.can_phone,
                        'avatar': candidate.can_avatar
                    },
                    'applications': []
                }
            
            # # Lấy thông tin stages cho candidate này
            # stages = frappe.get_all('Candidate Stages', 
            #                       filters={'parent': candidate.candidate_id},
            #                       fields=['stage_name', 'stage_status', 'stage_date'],
            #                       order_by='idx')
            
            # Lấy round history
            rounds = frappe.get_all('ATS_CandidateRoundHistory',
                                  filters={'parent': candidate.candidate_id},
                                  fields=['round_name', 'change_date', 'sync_id'],
                                  order_by='creation DESC')
            
            application_info = {
                'candidate_id': candidate.candidate_id,
                'can_id': candidate.can_id,
                'job_title': candidate.jo_public_title or candidate.jo_internal_title,
                'job_position': candidate.jo_position,
                'job_location': candidate.jo_location,
                'job_route': candidate.job_route,
                'application_status': candidate.status,
                'application_date': candidate.can_application_date,
                'job_status': candidate.job_status,
                'job_deadline': candidate.jo_application_deadline,
                'recruiter': candidate.can_recruiter,
                'source': candidate.candidatesource_id,
                # 'stages': stages,
                'rounds': rounds
            }
            
            candidate_groups[key]['applications'].append(application_info)
        
        # Format response
        response_data = []
        for group in candidate_groups.values():
            response_data.append(group)
        
        return {
            'success': True,
            'message': _("Tìm thấy {} ứng viên phù hợp").format(len(response_data)),
            'data': response_data,
            'total_applications': sum(len(group['applications']) for group in response_data)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Candidate Status Check Error")
        return {
            'success': False,
            'message': _("Có lỗi xảy ra khi kiểm tra thông tin ứng viên"),
            'error': str(e),
            'data': []
        }

@frappe.whitelist(allow_guest=True)
def get_candidate_detailed_info(candidate_id):
    """
    Get detailed information for a specific candidate
    
    Args:
        candidate_id (str): ATS_Candidate ID
    
    Returns:
        dict: Detailed candidate information
    """
    
    try:
        if not candidate_id:
            return {
                'success': False,
                'message': _("Candidate ID is required")
            }
        
        # Get candidate document
        candidate = frappe.get_doc('ATS_Candidate', candidate_id)
        
        # Get job opening details
        job_opening = None
        if candidate.job_opening_id:
            job_opening = frappe.get_doc('ATS_JobOpening', candidate.job_opening_id)
        
        # Format response
        result = {
            'success': True,
            'candidate': {
                'basic_info': {
                    'can_id': candidate.can_id,
                    'full_name': candidate.can_full_name,
                    'email': candidate.can_email,
                    'phone': candidate.can_phone,
                    'avatar': candidate.can_avatar,
                    'dob': candidate.can_dob,
                    'gender': candidate.can_gender,
                    'region': candidate.can_region,
                    'address': candidate.can_address,
                    'other_links': candidate.can_other_links
                },
                'job_info': {
                    'job_title': job_opening.jo_public_title if job_opening else None,
                    'job_position': job_opening.jo_position if job_opening else None,
                    'job_location': job_opening.jo_location if job_opening else None,
                    'application_status': candidate.status,
                    'application_date': candidate.can_application_date,
                    'recruiter': candidate.can_recruiter,
                    'collaborator': candidate.can_collaborator
                },
                'education': {
                    'education_level': candidate.educationlevel_id,
                    'institution': candidate.institution_id,
                    'major': candidate.major_id
                },
                'work_experience': candidate.candidate_work_experience,
                'projects': candidate.candidate_project,
                'certifications': candidate.candidate_certification,
                'skills': candidate.candidate_skill,
                'awards': candidate.candidate_award,
                'courses': candidate.candidate_course,
                'stages': candidate.candidate_stages,
                'round_history': candidate.round_history
            }
        }
        
        return result
        
    except frappe.DoesNotExistError:
        return {
            'success': False,
            'message': _("Không tìm thấy ứng viên")
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Candidate Detail Error")
        return {
            'success': False,
            'message': _("Có lỗi xảy ra khi lấy thông tin ứng viên"),
            'error': str(e)
        }

@frappe.whitelist(allow_guest=True)
def get_public_jobs():
    """
    Get list of published job openings for public view
    
    Returns:
        list: Published job openings
    """
    
    try:
        jobs = frappe.get_all('ATS_JobOpening',
                            filters={
                                'publish_to_career_page': 1,
                                'status': ['in', ['Open', 'Draft']]
                            },
                            fields=[
                                'name', 'jo_public_title', 'jo_internal_title',
                                'jo_position', 'jo_location', 'jo_work_form',
                                'jo_application_deadline', 'route', 'status',
                                'applicants_applied', 'jo_min_salary', 'jo_max_salary'
                            ],
                            order_by='creation DESC')
        
        return {
            'success': True,
            'jobs': jobs
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Public Jobs Error")
        return {
            'success': False,
            'message': _("Có lỗi xảy ra khi lấy danh sách công việc"),
            'error': str(e)
        } 
        
        
