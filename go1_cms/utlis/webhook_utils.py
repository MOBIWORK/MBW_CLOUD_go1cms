import requests
import frappe
import hashlib
import hmac
import json
from datetime import datetime
from frappe import as_json

def forward_webhook(doc_data):
    webhook_url = frappe.conf.get("webhook_base_url")
    secret = frappe.conf.get("webhook_secret", "default_secret")
    
    # Use full doc_data for signature calculation với format giống ATS
    payload_json = json.dumps(doc_data, default=str, separators=(',', ':'), sort_keys=True)

    # Tính HMAC signature
    signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload_json.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not webhook_url:
        log_webhook_result("Unknown", "Unknown", "forward", "Error", "Missing webhook_base_url in config", doc_data)
        frappe.log_error("Missing external_webhook_url in config")
        return
        
    headers={
        "X-Signature": signature,
        "Content-Type": "application/json",
        "Expect": ""  # Ngăn chặn header Expect: 100-continue
    }
    url = f"{webhook_url}/api/method/mbw_ats.webhook.cms.receive_webhook"
    
    # Extract info for logging
    records = doc_data.get("records", [])
    ref_doctype = doc_data.get("doctype", "Unknown")
    sync_id = records[0].get("sync_id", "Unknown") if records else "Unknown"
    action = records[0].get("action", "Unknown") if records else "Unknown"
    
    try:
        # Sử dụng session để tránh vấn đề với connection pooling
        session = requests.Session()
        session.headers.update(headers)
        res = session.post(url, data=payload_json, timeout=30)
        res.raise_for_status()
        
        log_webhook_result(ref_doctype, sync_id, action, "Success", f"HTTP {res.status_code}", doc_data)
        frappe.logger("Webhook").info(f"Forwarded to external system: {res.status_code}")
        
    except Exception as e:
        error_msg = str(e)
        log_webhook_result(ref_doctype, sync_id, action, "Error", error_msg[:500], doc_data)
        frappe.log_error(frappe.get_traceback(), "Webhook Forward Error")

def log_webhook_result(ref_doctype, sync_id, action, status, message, payload):
    """
    Lưu log kết quả xử lý webhook
    """
    try:
        frappe.get_doc({
            "doctype": "Webhook Log",
            "ref_doctype": ref_doctype,
            "sync_id": sync_id,
            "action": action.title(),
            "status": status.title(),
            "message": message[:500],
            "payload": json.dumps(payload, ensure_ascii=False, default=str),
            "timestamp": datetime.now()
        }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to log webhook: {e}")
