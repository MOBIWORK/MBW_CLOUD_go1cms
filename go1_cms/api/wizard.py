import frappe
import json
from frappe import _
from go1_cms.api.footer import (
    get_info_footer_component,
    update_info_footer_component,
)


@frappe.whitelist(allow_guest=True)
def mark_done():
    frappe.db.set_single_value("User Guide Settings", "hide_user_guide", 1)
    frappe.db.commit()
    return {"status": "success"}


@frappe.whitelist(allow_guest=True)
def should_show():
    hide_guide = frappe.db.get_single_value(
        "User Guide Settings", "hide_user_guide"
    )
    return {"show_guide": not bool(hide_guide)}


@frappe.whitelist(allow_guest=True)
def update_footer_from_onboarding_wizard(input_data):
    try:
        raw_data = frappe.local.form_dict.get('input_data')
        if isinstance(raw_data, str):
            input_data = json.loads(raw_data)
        else:
            input_data = raw_data
        # 1. Lấy dữ liệu footer hiện tại
        current_footer = get_info_footer_component()

        # 2. Merge dữ liệu từ OnboardingWizard.vue vào dict hiện tại
        # Ví dụ: gán các field cụ thể
        for section in current_footer["fields_st_cp"]:
            for field in section.get("fields", []):
                key = field.get("field_key")
                if key in input_data and input_data[key] is not None:
                    field["content"] = input_data[key]

        for section in current_footer["fields_cp"]:
            for field in section.get("fields", []):
                key = field.get("field_key")
                if key in input_data and input_data[key] is not None:
                    field["content"] = input_data[key]

        # 3. Gọi update_info_footer_component để lưu
        update_info_footer_component(current_footer)
        print(">>>>>>>>>>>>>>>>>>>:", current_footer)

        return {"status": "success"}

    except Exception as ex:
        frappe.log_error(
            message=str(ex), title="update_footer_from_onboarding_wizard error"
        )
        frappe.throw(_("An error has occurred"))
