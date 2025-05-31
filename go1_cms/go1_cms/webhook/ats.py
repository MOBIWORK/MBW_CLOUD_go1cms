import frappe
from go1_cms.utils.auth import secure_webhook
from frappe import _
#Sync lần đầu

@secure_webhook()
def ats_cate_parse():
    #Lấy dữ liệu từ request
    if frappe.request.method != "POST":
            frappe.throw(_("Only POST method is allowed"))
    data = frappe.request.data
    if not data:
        frappe.throw(_("No data received"))

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