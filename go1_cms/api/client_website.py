import frappe
from frappe import _
from frappe.model.document import get_controller
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_client_websites():
    filters = {}
    doctype = "MBW Client Website"
    columns = []
    rows_in_list = []
    rows = []
    order_by = "modified desc"

    _list = get_controller(doctype)
    if hasattr(_list, "default_list_data"):
        columns = _list.default_list_data().get("columns")
        rows = _list.default_list_data().get("rows")

    # check if rows has all keys from columns if not add them
    for column in columns:
        if column.get("key") not in rows:
            rows.append(column.get("key"))
        column["label"] = _(column.get("label"))

        if column.get("key") == "_liked_by" and column.get("width") == "10rem":
            column["width"] = "50px"
    rows_in_list = [row for row in rows]
    rows = [row for row in rows if row not in ['action_button']]

    data = frappe.db.get_all(
        doctype,
        fields=rows,
        filters=filters,
        order_by=order_by
    ) or []

    return {
        "data": data,
        "columns": columns,
        "rows": rows_in_list,
        "total_count": len(frappe.get_all(doctype, filters=filters)),
        "row_count": len(data),
    }


@frappe.whitelist()
@check_user_admin
def change_name_web_client_website(name, name_web):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("Website not found"), frappe.DoesNotExistError)
    if not name_web:
        frappe.throw(_("Name" + ' ' + _('cannot be empty')),
                     frappe.DoesNotExistError)

    frappe.db.set_value('MBW Client Website', name, 'name_web', name_web)

    return name


@frappe.whitelist()
@check_user_admin
def set_primary_client_website(name):
    if not frappe.db.exists({"doctype": "MBW Website Template", "name": name}):
        frappe.throw(_("Interface not found"), frappe.DoesNotExistError)

    web_template = frappe.db.get_value(
        'MBW Website Template', name, ['template_in_use', 'installed_template'], as_dict=1)
    if web_template.installed_template == 0:
        frappe.throw(_("Interface not installed"))
    if web_template.template_in_use == 1:
        frappe.throw(_("Interface already in use"))

    name_client_web = frappe.db.get_value(
        'MBW Client Website', {'setting_from_template': name}, ['name'])

    if not name_client_web:
        frappe.throw(_("Website not found"), frappe.DoesNotExistError)

    doc = frappe.get_doc('MBW Client Website', name_client_web)
    doc.type_web = 'Live version'
    doc.edit = 1
    doc.save(ignore_permissions=True)

    # update web template
    frappe.db.set_value('MBW Website Template', name, 'template_in_use', 1)
    existing_list = frappe.db.sql(
        '''UPDATE `tabMBW Website Template` SET template_in_use=0 WHERE name!="{web_name}" AND template_in_use=1'''.format(web_name=name))
    frappe.db.commit()

    return name


@frappe.whitelist()
@check_user_admin
def update_published_client_website(name, published):
    client_web = frappe.db.get_value(
        'MBW Client Website', {'setting_from_template': name}, ['name', 'published'], as_dict=1)
    if not client_web:
        frappe.throw(_("Website not found"), frappe.DoesNotExistError)

    if published == client_web.published:
        if published == 0:
            frappe.throw(_("The website has already been deactivated"))
        else:
            frappe.throw(_("The website has already been activated"))

    doc = frappe.get_doc('MBW Client Website', client_web.name)
    doc.published = published
    doc.save()

    return name


@frappe.whitelist()
@check_user_admin
def update_edit_client_website(name):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("Website not found"), frappe.DoesNotExistError)

    frappe.db.set_value('MBW Client Website', name, 'edit', 1)
    frappe.db.sql(
        '''UPDATE `tabMBW Client Website` SET edit=0 WHERE name!="{web_name}" AND edit=1'''.format(web_name=name))
    frappe.db.commit()

    return name


@frappe.whitelist()
@check_user_admin
def delete_client_website(name):
    try:
        name_client_web = frappe.db.get_value(
            'MBW Client Website', {'setting_from_template': name}, ['name'])
        if not name_client_web:
            frappe.throw(_("Website not found"), frappe.DoesNotExistError)

        frappe.delete_doc('MBW Client Website', name_client_web)

        web_template = frappe.get_doc('MBW Website Template', name)
        web_template_dict = web_template.as_dict()

        web_template.template_in_use = 0
        web_template.installed_template = 0

        # === comment: if keep template
        web_template.web_theme = None
        web_template.header_component = None
        web_template.footer_component = None
        web_template.page_templates = []
        web_template.flags.ignore_permissions = True
        web_template.flags.ignore_mandatory = True

        web_template.save()

        # === comment: if keep template
        # delete resource template
        for temp in web_template_dict.page_templates:
            frappe.delete_doc('Page Template', temp.page_template)
        if web_template_dict.web_theme:
            frappe.delete_doc('Web Theme', web_template_dict.web_theme)
        if web_template_dict.header_component:
            frappe.delete_doc('Header Component',
                              web_template_dict.header_component)
        if web_template_dict.footer_component:
            frappe.delete_doc('Footer Component',
                              web_template_dict.footer_component)

        return name
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except frappe.DoesNotExistError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex), frappe.DoesNotExistError)
    except Exception as ex:
        frappe.throw(_('An error has occurred'))
