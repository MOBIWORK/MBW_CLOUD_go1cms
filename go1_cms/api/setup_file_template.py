import frappe
from frappe import _
from go1_cms.api.common import (
    handle_write_multiple_files_web_template
)

from go1_cms.go1_cms.after_install import (
    after_install
)
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def create_file_json():
    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    if developer_mode == 0:
        frappe.throw(_("Không thể thực hiện"), frappe.PermissionError)

    # Export tất cả templates thành JSON files
    handle_write_multiple_files_web_template()
    
    # Log thành công
    frappe.log_error("Templates exported successfully to mbw_json_data folder", "create_file_json")
    
    return {
        'msg': "Đã export thành công các templates: Section Template, Page Template, Header Component, Footer Component, Web Theme, MBW Website Template"
    }


@frappe.whitelist()
@check_user_admin
def update_from_json():
    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    if developer_mode == 0:
        frappe.throw(_("Không thể thực hiện"), frappe.PermissionError)

    # Import templates từ JSON files
    update_templates_from_json()
    return {
        'msg': "Đã import thành công các templates từ JSON files vào database"
    }


def update_templates_from_json():
    """Update templates từ JSON files đã tạo"""
    from go1_cms.go1_cms.after_install import read_module_path_mbw
    
    # Các file template cần import
    template_files = [
        'section_template.json',
        'page_template.json', 
        'header_component.json',
        'footer_component.json',
        'web_theme.json',
        'mbw_website_template.json'
    ]
    
    frappe.log_error(f"Starting template import from JSON files", "update_templates_from_json")
    
    for file_name in template_files:
        try:
            frappe.log_error(f"Importing {file_name}", "update_templates_from_json")
            read_module_path_mbw(file_name)
            frappe.log_error(f"Successfully imported {file_name}", "update_templates_from_json")
        except Exception as e:
            frappe.log_error(f"Error importing {file_name}: {str(e)}", "update_templates_from_json")
            continue
    
    frappe.log_error("Template import completed", "update_templates_from_json")
