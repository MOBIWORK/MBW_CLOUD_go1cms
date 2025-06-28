# Copyright (c) 2024, xxx and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import random_string


class MBW_ATSFieldsLayout(Document):
	pass
# @frappe.whitelist()
# def get_fields_layout(doctype: str, type: str):
#     # print("Test log get_fields_layout doctype :  ", doctype)
#     # print("Test log get_fields_layout type :  ", type)
#     sections = []
#     if frappe.db.exists("MBW_ATS Fields Layout", {"dt": doctype, "type": type}):
#         layout = frappe.get_doc("MBW_ATS Fields Layout", {"dt": doctype, "type": type})
#     else:
#         return []

#     if layout.layout:
#         sections = json.loads(layout.layout)

#     allowed_fields = []
#     for section in sections:
#         if not section.get("fields"):
#             continue
#         allowed_fields.extend(section.get("fields"))

#     fields = frappe.get_meta(doctype).fields
#     fields = [field for field in fields if field.fieldname in allowed_fields]
#     # print("Test log get_fields_layout fields 1 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>:  ", fields)
	
#     for section in sections:
#         for field in section.get("fields") if section.get("fields") else []:
#             field = next((f for f in fields if f.fieldname == field), None)
#             if field:
#                 ops= field.options
#                 if field.fieldtype == "Select" and field.options:
#                     ops = [] if not field.options else  field.options.split("\n")
#                         # Chuyển đổi các tùy chọn trong field.options thành danh sách
						
#                     # list_options = field.options.split("\n")
#                     ops = [{"label": _(option), "value": option} for option in ops]
#                     # Chỉ thêm giá trị trống nếu không phải là trường bắt buộc
#                     if not field.reqd:
#                         ops.insert(0, {"label": "", "value": ""})
					
#                 field = {
#                     "label": _(field.label),
#                     "name": field.fieldname,
#                     "type": field.fieldtype,
#                     "options": ops,
#                     "mandatory": field.reqd,
#                     "default": field.default,
#                     "placeholder": field.get("placeholder"),
#                     "filters": field.get("link_filters"),
#                     "all_properties": field,
#                 }
#                 section["fields"][section.get("fields").index(field["name"])] = field
#     # print("Test log get_fields_layout sections 2 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>:  ", sections)
#     return sections or []

@frappe.whitelist()
def get_fields_layout(doctype: str, type: str, parent_doctype: str | None = None):
	tabs = []
	layout = None

	if frappe.db.exists("MBW_ATS Fields Layout", {"dt": doctype, "type": type}):
		layout = frappe.get_doc("MBW_ATS Fields Layout", {"dt": doctype, "type": type})

	if layout and layout.layout:
		tabs = json.loads(layout.layout)
	if not tabs:
		tabs = get_default_layout(doctype)

	print("Test log get_fields_layout tabs :  ", tabs)
	has_tabs = tabs[0].get("sections") if tabs and tabs[0] else False

	if not has_tabs:
		tabs = [{"name": "first_tab", "sections": tabs}]

	allowed_fields = []
	for tab in tabs:
		for section in tab.get("sections"):
			if "columns" not in section:
				continue
			for column in section.get("columns"):
				if not column.get("fields"):
					continue
				allowed_fields.extend(column.get("fields"))

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldname in allowed_fields]

	for tab in tabs:
		for section in tab.get("sections"):
			for column in section.get("columns") if section.get("columns") else []:
				for field in column.get("fields") if column.get("fields") else []:
					field = next((f for f in fields if f.fieldname == field), None)
					if field:
						field = field.as_dict()
						handle_perm_level_restrictions(field, doctype, parent_doctype)
						column["fields"][column.get("fields").index(field["fieldname"])] = field

	return tabs or []

@frappe.whitelist()
def get_sidepanel_sections(doctype):
	if not frappe.db.exists("MBW_ATS Fields Layout", {"dt": doctype, "type": "Side Panel"}):
		return []
	layout = frappe.get_doc("MBW_ATS Fields Layout", {"dt": doctype, "type": "Side Panel"}).layout

	if not layout:
		return []

	layout = json.loads(layout)

	not_allowed_fieldtypes = [
		"Tab Break",
		"Section Break",
		"Column Break",
	]

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in not_allowed_fieldtypes]

	for section in layout:
		section["name"] = section.get("name") or section.get("label")
		for column in section.get("columns") if section.get("columns") else []:
			for field in column.get("fields") if column.get("fields") else []:
				field_obj = next((f for f in fields if f.fieldname == field), None)
				if field_obj:
					field_obj = field_obj.as_dict()
					handle_perm_level_restrictions(field_obj, doctype)
					column["fields"][column.get("fields").index(field)] = get_field_obj(field_obj)

	fields_meta = {}
	for field in fields:
		fields_meta[field.fieldname] = field

	return layout

def handle_perm_level_restrictions(field, doctype, parent_doctype=None):
	if field.permlevel == 0:
		return
	field_has_write_access = field.permlevel in get_permlevel_access("write", doctype, parent_doctype)
	field_has_read_access = field.permlevel in get_permlevel_access("read", doctype, parent_doctype)

	if not field_has_write_access and field_has_read_access:
		field.read_only = 1
	if not field_has_read_access and not field_has_write_access:
		field.hidden = 1
  
def get_permlevel_access(permission_type="write", doctype=None, parent_doctype=None):
	allowed_permlevels = []
	roles = frappe.get_roles()

	meta = frappe.get_meta(doctype)

	if meta.istable and parent_doctype:
		meta = frappe.get_meta(parent_doctype)
	elif meta.istable and not parent_doctype:
		return [1, 0]

	for perm in meta.permissions:
		if perm.role in roles and perm.get(permission_type) and perm.permlevel not in allowed_permlevels:
			allowed_permlevels.append(perm.permlevel)

	return allowed_permlevels

def get_field_obj(field):
	field["placeholder"] = field.get("placeholder") or "Add " + field.label + "..."

	if field.fieldtype == "Link":
		field["placeholder"] = field.get("placeholder") or "Select " + field.label + "..."
	elif field.fieldtype == "Select" and field.options:
		field["placeholder"] = field.get("placeholder") or "Select " + field.label + "..."
		field["options"] = [{"label": option, "value": option} for option in field.options.split("\n")]

	if field.read_only:
		field["tooltip"] = "This field is read only and cannot be edited."

	return field


@frappe.whitelist()
def save_fields_layout(doctype: str, type: str, layout: str):
	if frappe.db.exists("MBW_ATS Fields Layout", {"dt": doctype, "type": type}):
		doc = frappe.get_doc("MBW_ATS Fields Layout", {"dt": doctype, "type": type})
	else:
		doc = frappe.new_doc("MBW_ATS Fields Layout")

	doc.update({
		"dt": doctype,
		"type": type,
		"layout": layout,
	})
	doc.save(ignore_permissions=True)

	return doc.layout

# lay default giong nhu layout cua doctype
# def get_default_layout(doctype: str):
# 	fields = frappe.get_meta(doctype).fields

# 	tabs = []

# 	if fields and fields[0].fieldtype not in ("Tab Break", "Section Break"):
# 		sections = [{
# 			"name": "section_" + str(random_string(4)),
# 			"columns": [{"name": "column_" + str(random_string(4)), "fields": []}],
# 	}]
# 	tabs.append({"name": "tab_" + str(random_string(4)), "sections": sections})

# 	for field in fields:
# 		if field.fieldtype == "Tab Break":
# 			tabs.append(
# 				{
# 					"name": "tab_" + str(random_string(4)),
# 					"label": field.label,
# 					"sections": [
# 						{
# 							"name": "section_" + str(random_string(4)),
# 							"columns": [{"name": "column_" + str(random_string(4)), "fields": []}],
# 						}
# 					],
# 				}
# 			)
# 		elif field.fieldtype == "Section Break":
# 			tabs[-1]["sections"].append(
# 				{
# 					"name": "section_" + str(random_string(4)),
# 					"label": field.label,
# 					"columns": [{"name": "column_" + str(random_string(4)), "fields": []}],
# 				}
# 			)
# 		elif field.fieldtype == "Column Break":
# 			tabs[-1]["sections"][-1]["columns"].append(
# 				{"name": "column_" + str(random_string(4)), "fields": []}
# 			)
# 		else:
# 			tabs[-1]["sections"][-1]["columns"][-1]["fields"].append(field.fieldname)

# 	return tabs

def get_default_layout(doctype: str):
    fields = frappe.get_meta(doctype).fields
    tabs = []
    current_tab = None
    current_section = None
    current_column = None

    for field in fields:
        if field.fieldtype == "Tab Break":
            current_tab = {
                "name": "tab_" + str(random_string(4)),
                "label": field.label,
                "sections": []
            }
            tabs.append(current_tab)
            current_section = None  # reset section và column khi bắt đầu tab mới
            current_column = None
        elif field.fieldtype == "Section Break":
            if not current_tab:
                # Nếu chưa có tab, tạo tab mặc định
                current_tab = {"name": "tab_" + str(random_string(4)), "sections": []}
                tabs.append(current_tab)
            current_section = {
                "name": "section_" + str(random_string(4)),
                "label": field.label,
                "columns": []
            }
            current_tab["sections"].append(current_section)
            current_column = None
        elif field.fieldtype == "Column Break":
            if not current_section:
                # Nếu chưa có section, tạo section mặc định
                current_section = {"name": "section_" + str(random_string(4)), "columns": []}
                if not current_tab:
                    current_tab = {"name": "tab_" + str(random_string(4)), "sections": [current_section]}
                    tabs.append(current_tab)
                else:
                    current_tab["sections"].append(current_section)
            current_column = {"name": "column_" + str(random_string(4)), "fields": []}
            current_section["columns"].append(current_column)
        else:
            # Với các trường thường, đảm bảo rằng có tab, section và column để thêm dữ liệu
            if not current_tab:
                current_tab = {"name": "tab_" + str(random_string(4)), "sections": []}
                tabs.append(current_tab)
            if not current_section:
                current_section = {"name": "section_" + str(random_string(4)), "columns": []}
                current_tab["sections"].append(current_section)
            if not current_column:
                current_column = {"name": "column_" + str(random_string(4)), "fields": []}
                current_section["columns"].append(current_column)
            current_column["fields"].append(field.fieldname)

    return tabs

