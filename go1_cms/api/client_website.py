import frappe
from frappe import _
from frappe.model.document import get_controller
from go1_cms.api.wrapper_api import (
    check_user_admin
)


def delete_mobile_page_sections_for_template(page_template_name):
    """Delete all Mobile Page Sections linked to a specific Page Template"""
    try:
        # Get all Mobile Page Sections linked to this Page Template
        mobile_sections = frappe.db.get_all(
            "Mobile Page Section", 
            filters={
                "parent": page_template_name, 
                "parenttype": "Page Template"
            },
            fields=["name", "section"]
        )
        
        deleted_count = 0
        for section in mobile_sections:
            try:
                # Delete the associated Page Section first if it exists
                if section.section and frappe.db.exists("Page Section", section.section):
                    frappe.delete_doc("Page Section", section.section, ignore_permissions=True)
                    print(f"  🗑️  Deleted Page Section: {section.section}")
                
                # Delete the Mobile Page Section
                frappe.delete_doc("Mobile Page Section", section.name, ignore_permissions=True)
                deleted_count += 1
                print(f"  🗑️  Deleted Mobile Page Section: {section.name}")
                
            except Exception as e:
                print(f"  ⚠️  Error deleting Mobile Page Section {section.name}: {str(e)}")
                # Continue with other sections even if one fails
                
        frappe.db.commit()
        return deleted_count
        
    except Exception as e:
        print(f"⚠️  Error in delete_mobile_page_sections_for_template: {str(e)}")
        return 0


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
        print(f"🗑️  Deleting Page Templates and dependencies for template: {name}")
        
        for temp in web_template_dict.page_templates:
            try:
                page_template_name = temp.page_template
                print(f"📄 Processing Page Template: {page_template_name}")
                
                # First, delete Mobile Page Sections linked to this Page Template
                deleted_sections_count = delete_mobile_page_sections_for_template(page_template_name)
                print(f"  🗑️  Deleted {deleted_sections_count} Mobile Page Sections")
                
                # Then delete the Page Template itself
                frappe.delete_doc('Page Template', page_template_name, ignore_permissions=True)
                print(f"  ✅ Deleted Page Template: {page_template_name}")
                
            except frappe.DoesNotExistError:
                print(f"  ⚠️  Page Template {page_template_name} already deleted or not found")
            except Exception as e:
                print(f"  ❌ Error deleting Page Template {page_template_name}: {str(e)}")
                # Continue with other templates even if one fails
                
        # Trước khi xóa, cần unlink các references trong Web Theme để tránh validation error
        if web_template_dict.web_theme:
            try:
                # Clear references trong Web Theme trước khi xóa components
                web_theme_doc = frappe.get_doc('Web Theme', web_template_dict.web_theme)
                web_theme_doc.default_header = None
                web_theme_doc.default_footer = None
                web_theme_doc.flags.ignore_permissions = True
                web_theme_doc.save()
                print(f"✅ Cleared references in Web Theme: {web_template_dict.web_theme}")
            except Exception as e:
                print(f"⚠️  Error clearing Web Theme references: {str(e)}")
        
        # Clear tất cả references đến Header/Footer Components từ các Web Themes khác
        if web_template_dict.header_component:
            try:
                # Tìm tất cả Web Themes có reference đến Header Component này
                themes_with_header = frappe.db.get_all('Web Theme', 
                    filters={'default_header': web_template_dict.header_component}, 
                    fields=['name'])
                for theme in themes_with_header:
                    frappe.db.set_value('Web Theme', theme.name, 'default_header', None)
                    print(f"  🔗 Cleared header reference from Web Theme: {theme.name}")
                frappe.db.commit()
            except Exception as e:
                print(f"⚠️  Error clearing header references: {str(e)}")
                
        if web_template_dict.footer_component:
            try:
                # Tìm tất cả Web Themes có reference đến Footer Component này
                themes_with_footer = frappe.db.get_all('Web Theme', 
                    filters={'default_footer': web_template_dict.footer_component}, 
                    fields=['name'])
                for theme in themes_with_footer:
                    frappe.db.set_value('Web Theme', theme.name, 'default_footer', None)
                    print(f"  🔗 Cleared footer reference from Web Theme: {theme.name}")
                frappe.db.commit()
            except Exception as e:
                print(f"⚠️  Error clearing footer references: {str(e)}")

        # Bây giờ có thể xóa Header và Footer Components một cách an toàn
        if web_template_dict.header_component:
            try:
                frappe.delete_doc('Header Component', web_template_dict.header_component, ignore_permissions=True, force=True)
                print(f"✅ Deleted Header Component: {web_template_dict.header_component}")
            except Exception as e:
                print(f"⚠️  Error deleting Header Component: {str(e)}")
                
        if web_template_dict.footer_component:
            try:
                frappe.delete_doc('Footer Component', web_template_dict.footer_component, ignore_permissions=True, force=True)
                print(f"✅ Deleted Footer Component: {web_template_dict.footer_component}")
            except Exception as e:
                print(f"⚠️  Error deleting Footer Component: {str(e)}")
                
        # Cuối cùng, xóa Web Theme
        if web_template_dict.web_theme:
            try:
                frappe.delete_doc('Web Theme', web_template_dict.web_theme, ignore_permissions=True)
                print(f"✅ Deleted Web Theme: {web_template_dict.web_theme}")
            except Exception as e:
                print(f"⚠️  Error deleting Web Theme: {str(e)}")

        return name
    except frappe.ValidationError as ex:
        print("ValidationError:", str(ex))
        print("Traceback:", frappe.get_traceback())
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except frappe.DoesNotExistError as ex:
        
        frappe.clear_last_message()
        frappe.throw(str(ex), frappe.DoesNotExistError)
    except Exception as ex:
        frappe.throw(_('An error has occurred'))
