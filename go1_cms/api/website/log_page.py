import frappe
from frappe import _, local
from datetime import datetime
from go1_cms.api.menu import (
    get_menu_suggest
)


def log_page_view(ip, form_type=''):
    frappe.get_doc({
        'doctype': 'CMS Totals Signed Form',
        'ip': ip,
        'form_type': form_type,
        'time_request': datetime.now()
    }).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def log_page_session(session_id, path_url):
    ip = local.request.remote_addr
    ses_name = frappe.db.exists('CMS Session', [
        ['ip', '=', ip], ['session_id', '=', session_id]])

    if not ses_name:
        frappe.get_doc({
            'doctype': 'CMS Session',
            'session_id': session_id,
            'ip': ip,
            'time_access': datetime.now(),
            'link_site_access': path_url
        }).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def log_page_access(session_id, path_url, page=""):
    ip = local.request.remote_addr
    site_type = ''

    if page == "/":
        page = '/home'

    site_title = next((item for item in get_menu_suggest()
                      if item["redirect_url"] == page), {})
    site_title = site_title.get('menu_label')

    if page.startswith('/') and len(page):
        page = page[1:]

    if not site_title:
        blog = frappe.db.get_all("Mbw Blog Post", filters=[
                                 ['route', '=', page]], pluck='title', page_length=1)
        if blog:
            site_type = 'Tin tức'
            site_title = blog[0]
    if not site_title:
        job = frappe.db.get_all("Job Opening", filters=[
            ['route', '=', page]], pluck='job_title', page_length=1)
        if job:
            site_type = 'Tìm việc'
            site_title = job[0]

    frappe.get_doc({
        'doctype': 'CMS Access',
        'session_id': session_id,
        'ip': ip,
        'time_access': datetime.now(),
        'site_title': site_title,
        'site_type': site_type,
        'link_site_access': path_url,
        'route': page
    }).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def log_page_leave(session_id, path_url, active, session_old=None):
    ip = local.request.remote_addr
    if session_old:
        session_name = frappe.db.exists('CMS Session', [
            ['ip', '=', ip], ['session_id', '=', session_old]])
        doc = frappe.get_doc('CMS Session', session_name)
        doc.active = 0
        doc.save(ignore_permissions=True)

    session_name = frappe.db.exists('CMS Session', [
        ['ip', '=', ip], ['session_id', '=', session_id]])
    if session_name:
        doc = frappe.get_doc('CMS Session', session_name)
        doc.time_out = datetime.now()
        doc.active = active
        doc.save(ignore_permissions=True)
    else:
        frappe.get_doc({
            'doctype': 'CMS Session',
            'session_id': session_id,
            'ip': ip,
            'time_access': datetime.now(),
            'link_site_access': path_url,
            'active': 1
        }).insert(ignore_permissions=True)
