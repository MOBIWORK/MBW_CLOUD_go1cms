import requests
import frappe
import hashlib
import hmac
import json
from datetime import datetime

def forward_webhook(doc_data):
    webhook_url = frappe.conf.get("webhook_base_url")
    secret = frappe.conf.get("webhook_secret", "default_secret")
    signature = hmac.new(secret.encode('utf-8'), json.dumps(doc_data).encode('utf-8'), hashlib.sha256).hexdigest()
    if not webhook_url:
        frappe.log_error("Missing external_webhook_url in config")
        return
    headers={
        "X-Signature": signature,
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(webhook_url, json=doc_data,headers=headers, timeout=5)
        res.raise_for_status()
        frappe.logger("Webhook").info(f"Forwarded to external system: {res.status_code}")
    except Exception as e:
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
            "payload": json.dumps(payload, ensure_ascii=False),
            "timestamp": datetime.now()
        }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to log webhook: {e}")
