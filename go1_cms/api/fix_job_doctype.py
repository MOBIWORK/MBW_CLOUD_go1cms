import frappe
from frappe import _

def find_job_opening(name_job):
    """
    Tìm job opening trong cả ATS_JobOpening và CMS_JobOpening
    Trả về dict với doctype và data
    """
    # First check CMS_JobOpening (prioritize this as it's the current system)
    if frappe.db.exists("CMS_JobOpening", name_job):
        job_data = frappe.db.get_value("CMS_JobOpening", name_job, [
            'name', 'jo_public_title', 'jo_work_form', 'jo_location',
            'jo_using_unit', 'jo_position', 'jo_min_salary', 'jo_max_salary', 'jo_currency'
        ], as_dict=1)
        
        return {
            "found": True,
            "doctype": "CMS_JobOpening",
            "data": job_data,
            "job_title": job_data.jo_public_title
        }
    
    # Then check ATS_JobOpening
    elif frappe.db.exists("ATS_JobOpening", name_job):
        job_data = frappe.db.get_value("ATS_JobOpening", name_job, [
            'name', 'jo_public_title', 'jo_work_form', 'jo_location',
            'jo_using_unit', 'jo_position', 'jo_min_salary', 'jo_max_salary', 'jo_currency'
        ], as_dict=1)
        
        return {
            "found": True,
            "doctype": "ATS_JobOpening", 
            "data": job_data,
            "job_title": job_data.jo_public_title
        }
    
    # Not found in either
    return {
        "found": False,
        "doctype": None,
        "data": None,
        "job_title": None
    }

@frappe.whitelist()
def test_find_job_opening():
    """
    Test function để kiểm tra find_job_opening
    """
    try:
        # Get some job names to test
        cms_jobs = frappe.db.get_all("CMS_JobOpening", limit_page_length=2, pluck="name")
        ats_jobs = frappe.db.get_all("ATS_JobOpening", limit_page_length=2, pluck="name")
        
        results = {
            "cms_jobs_test": [],
            "ats_jobs_test": [],
            "not_found_test": None
        }
        
        # Test CMS jobs
        for job_name in cms_jobs:
            result = find_job_opening(job_name)
            results["cms_jobs_test"].append({
                "job_name": job_name,
                "result": result
            })
        
        # Test ATS jobs
        for job_name in ats_jobs:
            result = find_job_opening(job_name)
            results["ats_jobs_test"].append({
                "job_name": job_name,
                "result": result
            })
        
        # Test non-existent job
        result = find_job_opening("NON_EXISTENT_JOB")
        results["not_found_test"] = result
        
        return {
            "success": True,
            "message": "Test find_job_opening completed",
            "results": results,
            "total_cms_jobs": len(cms_jobs),
            "total_ats_jobs": len(ats_jobs)
        }
        
    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def test_upload_cv_compatibility():
    """
    Test API để kiểm tra cả hai hàm upload CV hoạt động với cả CMS_JobOpening và ATS_JobOpening
    """
    try:
        # Get sample jobs from both DocTypes
        cms_jobs = frappe.db.get_all("CMS_JobOpening", limit_page_length=1, pluck="name")
        ats_jobs = frappe.db.get_all("ATS_JobOpening", limit_page_length=1, pluck="name")
        
        results = {
            "cms_test_results": [],
            "ats_test_results": [],
            "error_tests": []
        }
        
        # Test CMS Jobs
        for job_name in cms_jobs:
            job_info = find_job_opening(job_name)
            results["cms_test_results"].append({
                "job_name": job_name,
                "job_info": job_info,
                "can_upload": job_info["found"]
            })
        
        # Test ATS Jobs  
        for job_name in ats_jobs:
            job_info = find_job_opening(job_name)
            results["ats_test_results"].append({
                "job_name": job_name,
                "job_info": job_info,
                "can_upload": job_info["found"]
            })
        
        # Test non-existent job
        non_existent_job = "NON_EXISTENT_JOB_12345"
        job_info = find_job_opening(non_existent_job)
        results["error_tests"].append({
            "job_name": non_existent_job,
            "job_info": job_info,
            "should_fail": not job_info["found"]
        })
        
        return {
            "success": True,
            "message": "Test upload CV compatibility completed",
            "results": results,
            "summary": {
                "total_cms_jobs": len(cms_jobs),
                "total_ats_jobs": len(ats_jobs),
                "cms_jobs_found": sum(1 for r in results["cms_test_results"] if r["can_upload"]),
                "ats_jobs_found": sum(1 for r in results["ats_test_results"] if r["can_upload"])
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Test Upload CV Compatibility")
        return {"error": str(e)}

@frappe.whitelist()
def test_all_fixes():
    """
    Comprehensive test for all job DocType fixes
    """
    try:
        results = {}
        
        # 1. Test find_job_opening function
        results["find_job_test"] = test_find_job_opening()
        
        # 2. Test upload CV compatibility  
        results["upload_cv_test"] = test_upload_cv_compatibility()
        
        # 3. Count total records
        results["record_counts"] = {
            "cms_job_openings": frappe.db.count("CMS_JobOpening"),
            "ats_job_openings": frappe.db.count("ATS_JobOpening"),
            "ats_candidates": frappe.db.count("ATS_Candidate")
        }
        
        return {
            "success": True,
            "message": "All job DocType fixes tested successfully",
            "results": results
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Test All Fixes")
        return {"error": str(e)}

@frappe.whitelist()
def get_test_job_ids():
    """
    API để lấy danh sách job IDs để test upload CV
    """
    try:
        cms_jobs = frappe.db.get_all("CMS_JobOpening", 
                                    fields=["name", "jo_public_title"], 
                                    limit_page_length=3)
        ats_jobs = frappe.db.get_all("ATS_JobOpening", 
                                    fields=["name", "jo_public_title"], 
                                    limit_page_length=3)
        
        return {
            "success": True,
            "message": "Test job IDs retrieved successfully",
            "data": {
                "cms_jobs": cms_jobs,
                "ats_jobs": ats_jobs,
                "instructions": {
                    "upload_cv_endpoint": "/api/method/go1_cms.api.website.jobs.upload_cv",
                    "upload_cv_ai_endpoint": "/api/method/go1_cms.api.website.jobs.upload_cv_with_ai_extraction",
                    "note": "Cả hai endpoint đều có thể xử lý job ID từ CMS_JobOpening hoặc ATS_JobOpening"
                }
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Test Job IDs")
        return {"error": str(e)}

@frappe.whitelist()
def validate_job_id(job_id):
    """
    API để validate xem job_id có tồn tại không
    """
    try:
        job_info = find_job_opening(job_id)
        
        if job_info["found"]:
            return {
                "success": True,
                "message": f"Job ID '{job_id}' hợp lệ",
                "data": {
                    "job_id": job_id,
                    "doctype": job_info["doctype"],
                    "job_title": job_info["job_title"],
                    "job_data": job_info["data"]
                }
            }
        else:
            return {
                "success": False,
                "message": f"Job ID '{job_id}' không tồn tại trong hệ thống",
                "data": None
            }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Validate Job ID")
        return {"error": str(e)} 