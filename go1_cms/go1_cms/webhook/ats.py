import frappe
from go1_cms.utlis.auth import secure_webhook
from go1_cms.go1_cms.webhook.handler import parse_webhook_data_batch
from frappe import _
import json

# Sync lần đầu


@secure_webhook(require_hmac=True)
def receive_webhook():
    """
    API nhận webhook dạng batch, sử dụng sync_id làm key định danh.
    Payload yêu cầu:
    {
        "doctype": "ATS_Candidate",
        "records": [ {...}, {...}, ... ]
    }
    """
    try:
        payload = frappe.request.get_json()

        # Kiểm tra định dạng tối thiểu
        if not payload or "doctype" not in payload or "records" not in payload:
            frappe.throw(_("Invalid payload: require 'doctype' and 'records'"))

        # Gọi xử lý batch
        # Gửi webhook
        frappe.enqueue(
            "go1_cms.go1_cms.webhook.handler.parse_webhook_data_batch",
            queue="short",
            timeout=300,
            now=True,
            payload=payload,
        )
        # results = parse_webhook_data_batch(payload)

        return {"status": "completed"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Webhook Receive Error: " + str(e))
        return {"status": "error", "message": str(e)}


@secure_webhook()
def ats_job_parse():
    if frappe.request.method != "POST":
        frappe.throw(_("Only POST method is allowed"))
    data = frappe.request.data
    if not data:
        frappe.throw(_("No data received"))


@secure_webhook()
def ats_candidate_parse():
    if frappe.request.method != "POST":
        frappe.throw(_("Only POST method is allowed"))
    data = frappe.request.data
    if not data:
        frappe.throw(_("No data received"))
