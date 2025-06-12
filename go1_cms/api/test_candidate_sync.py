import frappe
import uuid
import json
from frappe import _

@frappe.whitelist()
def test_candidate_sync_status():
    """
    Test API để kiểm tra trạng thái sync candidate
    """
    try:
        # Check webhook configuration
        webhook_config = {
            "webhook_base_url": frappe.conf.get("webhook_base_url"),
            "webhook_secret": frappe.conf.get("webhook_secret"),
            "api_token": frappe.conf.get("api_token")
        }
        
        # Check recent candidates with sync_id
        recent_candidates = frappe.db.get_all(
            "ATS_Candidate",
            fields=["name", "can_full_name", "can_email", "sync_id", "creation"],
            order_by="creation desc",
            limit_page_length=5
        )
        
        # Check webhook flags
        webhook_flags = {
            "ignore_webhook_sync": getattr(frappe.flags, "ignore_webhook_sync", None)
        }
        
        # Check webhook logs (if exists)
        webhook_logs = []
        try:
            webhook_logs = frappe.db.get_all(
                "Webhook Log", 
                fields=["name", "creation"],
                order_by="creation desc",
                limit_page_length=5
            )
        except Exception:
            # Webhook Log table might not exist
            webhook_logs = []
        
        return {
            "success": True,
            "message": "Candidate sync status retrieved",
            "data": {
                "webhook_config": webhook_config,
                "recent_candidates": recent_candidates,
                "webhook_flags": webhook_flags,
                "webhook_logs": webhook_logs,
                "candidate_count": frappe.db.count("ATS_Candidate")
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Test Candidate Sync Status")
        return {"error": str(e)}

@frappe.whitelist()
def create_test_candidate():
    """
    Tạo candidate test để kiểm tra sync
    """
    try:
        # Create test candidate
        test_candidate = frappe.new_doc('ATS_Candidate')
        test_candidate.can_id = f"TEST_{frappe.generate_hash(length=8)}"
        test_candidate.can_full_name = "Nguyễn Test Sync"
        test_candidate.can_email = f"test.sync.{frappe.generate_hash(length=6)}@example.com"
        test_candidate.can_phone = "0123456789"
        # Get first available job opening
        job_opening = frappe.db.get_value("CMS_JobOpening", {}, "jo_public_title") or "Default Job"
        test_candidate.job_opening_id = job_opening
        test_candidate.sync_id = str(uuid.uuid4())
        
        # Make sure sync is allowed
        frappe.flags.ignore_webhook_sync = False
        
        # Save candidate
        test_candidate.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Test candidate created successfully",
            "data": {
                "candidate_name": test_candidate.name,
                "candidate_id": test_candidate.can_id,
                "sync_id": test_candidate.sync_id,
                "webhook_flags": {
                    "ignore_webhook_sync": getattr(frappe.flags, "ignore_webhook_sync", None)
                }
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Test Candidate")
        return {"error": str(e)}

@frappe.whitelist()
def manual_sync_candidate(candidate_name):
    """
    Manually trigger sync for a candidate
    """
    try:
        if not frappe.db.exists("ATS_Candidate", candidate_name):
            return {"error": "Candidate not found"}
            
        candidate = frappe.get_doc("ATS_Candidate", candidate_name)
        
        # Trigger webhook manually
        from go1_cms.go1_cms.webhook.handler import handle_doc_event
        
        # Clear ignore flag
        frappe.flags.ignore_webhook_sync = False
        
        # Trigger sync
        handle_doc_event(candidate, "on_update")
        
        return {
            "success": True,
            "message": "Manual sync triggered",
            "data": {
                "candidate_name": candidate.name,
                "sync_id": candidate.sync_id,
                "webhook_triggered": True
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Manual Sync Candidate")
        return {"error": str(e)}

@frappe.whitelist()
def check_sync_configuration():
    """
    Check sync configuration and troubleshoot
    """
    try:
        issues = []
        
        # Check webhook base URL
        webhook_base_url = frappe.conf.get("webhook_base_url")
        if not webhook_base_url:
            issues.append("webhook_base_url not configured")
            
        # Check webhook secret
        webhook_secret = frappe.conf.get("webhook_secret")
        if not webhook_secret:
            issues.append("webhook_secret not configured")
            
        # Check hooks.py configuration
        from go1_cms.hooks import doc_events
        ats_candidate_hooks = doc_events.get("ATS_Candidate", {})
        if not ats_candidate_hooks.get("on_update"):
            issues.append("ATS_Candidate on_update hook not configured")
            
        # Check recent candidates without sync_id
        candidates_without_sync = frappe.db.get_all(
            "ATS_Candidate",
            fields=["name", "can_full_name"],
            filters=[["sync_id", "is", "not set"]],
            limit_page_length=5
        )
        
        if candidates_without_sync:
            issues.append(f"{len(candidates_without_sync)} candidates without sync_id")
            
        return {
            "success": True,
            "issues": issues,
            "config": {
                "webhook_base_url": webhook_base_url,
                "webhook_secret_configured": bool(webhook_secret),
                "hooks_configured": bool(ats_candidate_hooks.get("on_update")),
                "candidates_without_sync": len(candidates_without_sync)
            },
            "status": "OK" if not issues else "ISSUES_FOUND"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Sync Configuration")
        return {"error": str(e)}

@frappe.whitelist()
def fix_candidates_sync_id():
    """
    Add sync_id to candidates that don't have it
    """
    try:
        candidates_without_sync = frappe.db.get_all(
            "ATS_Candidate",
            fields=["name"],
            filters=[["sync_id", "is", "not set"]]
        )
        
        updated_count = 0
        for candidate in candidates_without_sync:
            sync_id = str(uuid.uuid4())
            frappe.db.set_value("ATS_Candidate", candidate.name, "sync_id", sync_id)
            updated_count += 1
            
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Added sync_id to {updated_count} candidates",
            "updated_count": updated_count
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Fix Candidates Sync ID")
        return {"error": str(e)}

@frappe.whitelist()
def check_webhook_logs():
    """
    Check webhook logs and error logs for sync issues
    """
    try:
        # Check recent webhook logs
        webhook_logs = frappe.db.get_all(
            "Webhook Log",
            fields=["name", "ref_doctype", "sync_id", "action", "status", "message", "creation"],
            order_by="creation desc",
            limit_page_length=10
        )
        
        # Check recent error logs related to webhook
        error_logs = frappe.db.get_all(
            "Error Log",
            fields=["name", "error", "creation"],
            filters=[["error", "like", "%webhook%"]],
            order_by="creation desc",
            limit_page_length=5
        )
        
        # Check recent error logs related to sync
        sync_error_logs = frappe.db.get_all(
            "Error Log", 
            fields=["name", "error", "creation"],
            filters=[["error", "like", "%sync%"]],
            order_by="creation desc",
            limit_page_length=5
        )
        
        return {
            "success": True,
            "data": {
                "webhook_logs": webhook_logs,
                "webhook_error_logs": error_logs,
                "sync_error_logs": sync_error_logs,
                "total_webhook_logs": len(webhook_logs),
                "total_error_logs": len(error_logs) + len(sync_error_logs)
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Webhook Logs")
        return {"error": str(e)}

@frappe.whitelist()
def test_webhook_connection():
    """
    Test webhook connection to ATS system
    """
    try:
        webhook_url = frappe.conf.get("webhook_base_url")
        if not webhook_url:
            return {"error": "webhook_base_url not configured"}
            
        # Test basic connectivity
        import requests
        test_url = f"{webhook_url}/api/method/ping"
        
        try:
            response = requests.get(test_url, timeout=5)
            connection_status = {
                "url": test_url,
                "status_code": response.status_code,
                "reachable": True,
                "response_time": "< 5s"
            }
        except requests.exceptions.RequestException as e:
            connection_status = {
                "url": test_url,
                "reachable": False,
                "error": str(e)
            }
            
        return {
            "success": True,
            "webhook_url": webhook_url,
            "connection_test": connection_status
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Test Webhook Connection")
        return {"error": str(e)} 