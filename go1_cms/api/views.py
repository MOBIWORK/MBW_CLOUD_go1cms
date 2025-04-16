import frappe
from pypika import Criterion
from go1_cms.api.wrapper_api import (
    check_user_admin
)
from go1_cms.api.common import (
    get_domain
)


@frappe.whitelist()
@check_user_admin
def get_views(doctype):
    if frappe.session.user == "Guest":
        frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

    check_doc = frappe.db.get_value('MBW Client Website', {'edit': 1})
    list_page = []
    name_web = ''
    open_add_new_page = False
    if check_doc:
        doc = frappe.db.get_value('MBW Client Website', check_doc, [
                                  'type_template', 'name_web'], as_dict=1)
        list_page = frappe.db.get_all("MBW Client Website Item", filters={
            "parent": check_doc, "parentfield": "page_websites", 'hidden': 0}, fields=['*'], order_by="idx"
        )
        name_web = doc.name_web

    for i in list_page:
        if i.page_type == "Trang mới":
            open_add_new_page = True
            break

    View = frappe.qb.DocType("CMS View Settings")
    query = (
        frappe.qb.from_(View)
        .select("*")
        .where(Criterion.any([View.user == '', View.user == frappe.session.user]))
    )
    if doctype:
        query = query.where(View.dt == doctype)
    views = query.run(as_dict=True)

    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')

    domain = get_domain()
    config_domain = {
        'domain': domain
    }

    result = {
        'website_primary': 1 if check_doc else 0,
        'list_page': list_page,
        'name_web': name_web,
        'views': views,
        'developer_mode': developer_mode,
        'config_domain': config_domain,
        'open_add_new_page': open_add_new_page
    }
    return result
