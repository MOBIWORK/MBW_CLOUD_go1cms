import frappe
from frappe import _

@frappe.whitelist()
def add_cms_meta_fields_to_cms_jobopening():
    """
    Thêm các field CMS meta (cms_meta_description, cms_meta_title, etc.) 
    vào DocType CMS_JobOpening để tránh lỗi AttributeError
    """
    try:
        doctype_name = "CMS_JobOpening"
        
        # Kiểm tra DocType có tồn tại không
        if not frappe.db.exists("DocType", doctype_name):
            return {"error": f"DocType {doctype_name} không tồn tại"}
        
        # Danh sách các custom fields cần thêm
        custom_fields = [
            {
                "fieldname": "cms_meta_section",
                "fieldtype": "Section Break",
                "label": "CMS Meta Information",
                "collapsible": 1,
                "insert_after": "route"
            },
            {
                "fieldname": "cms_meta_title",
                "fieldtype": "Data",
                "label": "Meta Title",
                "description": "Tiêu đề hiển thị trên search engine và social media",
                "insert_after": "cms_meta_section"
            },
            {
                "fieldname": "cms_meta_description",
                "fieldtype": "Text",
                "label": "Meta Description", 
                "description": "Mô tả hiển thị trên search engine và social media",
                "insert_after": "cms_meta_title"
            },
            {
                "fieldname": "column_break_cms_meta",
                "fieldtype": "Column Break",
                "insert_after": "cms_meta_description"
            },
            {
                "fieldname": "cms_meta_keywords",
                "fieldtype": "Text",
                "label": "Meta Keywords",
                "description": "Từ khóa SEO, phân cách bằng dấu phẩy",
                "insert_after": "column_break_cms_meta"
            },
            {
                "fieldname": "cms_meta_image",
                "fieldtype": "Attach Image",
                "label": "Meta Image",
                "description": "Hình ảnh hiển thị khi share trên social media",
                "insert_after": "cms_meta_keywords"
            }
        ]
        
        created_fields = []
        updated_fields = []
        
        for field_data in custom_fields:
            # Tạo custom field data
            custom_field = {
                "doctype": "Custom Field",
                "dt": doctype_name,
                "fieldname": field_data["fieldname"],
                "fieldtype": field_data["fieldtype"],
                "label": field_data.get("label", ""),
                "description": field_data.get("description", ""),
                "insert_after": field_data.get("insert_after", ""),
                "collapsible": field_data.get("collapsible", 0),
                "allow_on_submit": 0,
                "ignore_user_permissions": 0,
                "ignore_xss_filter": 0,
                "in_global_search": 0,
                "in_list_view": 0,
                "in_standard_filter": 0,
                "no_copy": 0,
                "permlevel": 0,
                "print_hide": 1,
                "read_only": 0,
                "report_hide": 0,
                "reqd": 0,
                "search_index": 0,
                "unique": 0
            }
            
            # Kiểm tra xem custom field đã tồn tại chưa
            existing_field = frappe.db.exists("Custom Field", {
                "dt": doctype_name,
                "fieldname": field_data["fieldname"]
            })
            
            if existing_field:
                # Update existing field
                doc = frappe.get_doc("Custom Field", existing_field)
                for key, value in custom_field.items():
                    if key != "doctype" and hasattr(doc, key):
                        setattr(doc, key, value)
                doc.save(ignore_permissions=True)
                updated_fields.append(field_data["fieldname"])
            else:
                # Create new field
                doc = frappe.get_doc(custom_field)
                doc.insert(ignore_permissions=True)
                created_fields.append(field_data["fieldname"])
        
        # Clear DocType cache để field mới có hiệu lực
        frappe.clear_cache(doctype=doctype_name)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Đã thêm/cập nhật CMS meta fields thành công",
            "created_fields": created_fields,
            "updated_fields": updated_fields,
            "total_fields": len(custom_fields)
        }
        
    except Exception as e:
        import traceback
        frappe.log_error(frappe.get_traceback(), "add_cms_meta_fields_error")
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@frappe.whitelist()
def check_cms_meta_fields():
    """
    Kiểm tra xem các CMS meta fields đã có trong CMS_JobOpening chưa
    """
    try:
        doctype_name = "CMS_JobOpening"
        
        required_fields = [
            "cms_meta_title",
            "cms_meta_description", 
            "cms_meta_keywords",
            "cms_meta_image"
        ]
        
        # Lấy meta của DocType
        meta = frappe.get_meta(doctype_name)
        existing_fields = [field.fieldname for field in meta.fields]
        
        field_status = {}
        for field in required_fields:
            field_status[field] = {
                "exists": field in existing_fields,
                "in_custom_fields": frappe.db.exists("Custom Field", {
                    "dt": doctype_name,
                    "fieldname": field
                }) is not None
            }
        
        missing_fields = [field for field in required_fields if field not in existing_fields]
        
        return {
            "doctype": doctype_name,
            "required_fields": required_fields,
            "existing_fields": len([f for f in required_fields if f in existing_fields]),
            "missing_fields": missing_fields,
            "field_status": field_status,
            "all_fields_exist": len(missing_fields) == 0
        }
        
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def test_cms_jobopening_meta_access():
    """
    Test việc truy cập meta fields trên CMS_JobOpening records
    """
    try:
        # Lấy một record test
        job_names = frappe.db.get_all("CMS_JobOpening", limit_page_length=1, pluck="name")
        
        if not job_names:
            return {"error": "Không có CMS_JobOpening nào để test"}
        
        job_name = job_names[0]
        job_doc = frappe.get_doc("CMS_JobOpening", job_name)
        
        # Test truy cập các meta fields
        test_results = {}
        fields_to_test = ["cms_meta_title", "cms_meta_description", "cms_meta_keywords", "cms_meta_image"]
        
        for field in fields_to_test:
            try:
                # Test direct access
                value = getattr(job_doc, field, "NOT_FOUND")
                test_results[field] = {
                    "direct_access": "SUCCESS",
                    "value": value,
                    "has_value": bool(value and value != "NOT_FOUND")
                }
            except AttributeError as e:
                test_results[field] = {
                    "direct_access": "FAILED",
                    "error": str(e),
                    "has_value": False
                }
        
        return {
            "success": True,
            "test_doc": job_name,
            "results": test_results
        }
        
    except Exception as e:
        return {"error": str(e)} 