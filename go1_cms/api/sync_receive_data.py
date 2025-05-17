import frappe
import json
from frappe import _
from frappe.utils import now, cstr

@frappe.whitelist()
def receive_category_data():
    """
    Nhận và xử lý dữ liệu danh mục từ mbw_ats
    
    JSON Request:
    {
        "doctype": "ATS_Unit",
        "data": {...},  # Dữ liệu danh mục
        "sync_field": "name"  # Trường dùng để đồng bộ (thường là name)
    }
    """
    if frappe.request and frappe.request.method != "POST":
        return {
            "success": False,
            "message": "Phương thức không được hỗ trợ. Sử dụng POST."
        }
        
    try:
        # Lấy dữ liệu từ request
        request_data = json.loads(frappe.request.data) if frappe.request.data else frappe.local.form_dict
        
        if not request_data.get("doctype") or not request_data.get("data"):
            return {
                "success": False,
                "message": "Thiếu thông tin doctype hoặc dữ liệu danh mục"
            }
            
        doctype = request_data.get("doctype")
        data = request_data.get("data")
        sync_field = request_data.get("sync_field") or "name"
        
        # Kiểm tra DocType tồn tại
        if not frappe.db.exists("DocType", doctype):
            return {
                "success": False,
                "message": f"DocType {doctype} không tồn tại trong hệ thống go1_cms"
            }
            
        # Kiểm tra xem bản ghi đã tồn tại hay chưa
        if frappe.db.exists(doctype, {sync_field: data.get(sync_field)}):
            # Cập nhật bản ghi hiện có
            existing_doc = frappe.get_doc(doctype, {sync_field: data.get(sync_field)})
            
            # Xử lý đặc biệt cho doctype ATS_Unit nếu là dạng tree
            if doctype == "ATS_Unit" and data.get("parent_ats_unit"):
                # Kiểm tra nếu parent đã tồn tại trước khi cập nhật
                if not frappe.db.exists("ATS_Unit", {"name": data.get("parent_ats_unit")}):
                    return {
                        "success": False,
                        "message": f"Parent unit {data.get('parent_ats_unit')} chưa tồn tại. Cần đồng bộ parent trước."
                    }
            
            # Loại bỏ các trường không cần thiết
            fields_to_ignore = ["creation", "modified", "modified_by", "owner", "docstatus"]
            
            # Cập nhật từng trường trong dữ liệu
            for field, value in data.items():
                if field not in fields_to_ignore and field in [f.fieldname for f in existing_doc.meta.fields]:
                    existing_doc.set(field, value)
            
            # Đánh dấu là đang đồng bộ để tránh vòng lặp đồng bộ
            existing_doc.flags.ignore_permissions = True
            existing_doc.flags.ignore_links = True
            existing_doc.flags.ignore_validate = True
            existing_doc.flags.ignore_sync = True
            existing_doc.flags.ignore_mandatory = True
            existing_doc.from_sync = True
            
            # Lưu lại
            existing_doc.save()
            
            frappe.db.commit()
            
            return {
                "success": True,
                "message": f"Đã cập nhật {doctype} từ mbw_ats: {data.get(sync_field)}"
            }
        else:
            # Tạo bản ghi mới
            
            # Xử lý đặc biệt cho doctype ATS_Unit nếu là dạng tree
            if doctype == "ATS_Unit" and data.get("parent_ats_unit"):
                # Kiểm tra nếu parent đã tồn tại trước khi thêm mới
                if not frappe.db.exists("ATS_Unit", {"name": data.get("parent_ats_unit")}):
                    return {
                        "success": False,
                        "message": f"Parent unit {data.get('parent_ats_unit')} chưa tồn tại. Cần đồng bộ parent trước."
                    }
            
            # Tạo bản ghi mới
            new_doc = frappe.new_doc(doctype)
            
            # Loại bỏ các trường không cần thiết
            fields_to_ignore = ["creation", "modified", "modified_by", "owner", "docstatus"]
            
            # Copy từng trường trong dữ liệu
            for field, value in data.items():
                if field not in fields_to_ignore and field in [f.fieldname for f in new_doc.meta.fields]:
                    new_doc.set(field, value)
            
            # Đánh dấu là đang đồng bộ để tránh vòng lặp đồng bộ
            new_doc.flags.ignore_permissions = True
            new_doc.flags.ignore_links = True
            new_doc.flags.ignore_validate = True
            new_doc.flags.ignore_sync = True
            new_doc.flags.ignore_mandatory = True
            new_doc.from_sync = True
            
            # Lưu lại
            new_doc.insert()
            
            frappe.db.commit()
            
            return {
                "success": True,
                "message": f"Đã thêm mới {doctype} từ mbw_ats: {data.get(sync_field)}"
            }
            
    except Exception as e:
        frappe.logger("sync").error(f"Lỗi khi nhận dữ liệu danh mục từ mbw_ats: {str(e)}")
        frappe.log_error(frappe.get_traceback(), f"Lỗi nhận dữ liệu danh mục")
        return {
            "success": False,
            "message": f"Lỗi khi xử lý dữ liệu danh mục: {str(e)}"
        }


@frappe.whitelist()
def delete_category_data():
    """
    Xóa dữ liệu danh mục theo yêu cầu từ mbw_ats
    
    JSON Request:
    {
        "doctype": "ATS_Unit",
        "name": "UNIT-00001",
        "sync_field": "name"
    }
    """
    if frappe.request and frappe.request.method != "POST":
        return {
            "success": False,
            "message": "Phương thức không được hỗ trợ. Sử dụng POST."
        }
        
    try:
        # Lấy dữ liệu từ request
        request_data = json.loads(frappe.request.data) if frappe.request.data else frappe.local.form_dict
        
        if not request_data.get("doctype") or not request_data.get("name"):
            return {
                "success": False,
                "message": "Thiếu thông tin doctype hoặc name của bản ghi cần xóa"
            }
            
        doctype = request_data.get("doctype")
        name = request_data.get("name")
        sync_field = request_data.get("sync_field") or "name"
        
        # Kiểm tra DocType tồn tại
        if not frappe.db.exists("DocType", doctype):
            return {
                "success": False,
                "message": f"DocType {doctype} không tồn tại trong hệ thống go1_cms"
            }
        
        # Tìm bản ghi theo sync_field
        existing_doc = None
        if sync_field == "name":
            if frappe.db.exists(doctype, name):
                existing_doc = name
        else:
            # Tìm doc dựa vào trường sync_field
            records = frappe.get_all(doctype, filters={sync_field: name}, fields=["name"])
            if records:
                existing_doc = records[0].name
        
        if not existing_doc:
            return {
                "success": False,
                "message": f"Không tìm thấy {doctype} với {sync_field}={name} trong hệ thống go1_cms"
            }
            
        # Kiểm tra nếu là Unit (cấu trúc tree), cần kiểm tra xem có nút con không trước khi xóa
        if doctype == "ATS_Unit":
            children = frappe.get_all(doctype, filters={"parent_ats_unit": existing_doc})
            if children:
                frappe.logger("sync").warning(f"Không thể xóa {doctype} {existing_doc} vì còn {len(children)} nút con")
                return {
                    "success": False,
                    "message": f"Không thể xóa {doctype} {existing_doc} vì còn {len(children)} nút con"
                }
                
        # Xóa bản ghi
        frappe.delete_doc(doctype, existing_doc, ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Đã xóa {doctype} {name} từ go1_cms"
        }
            
    except Exception as e:
        frappe.logger("sync").error(f"Lỗi khi xóa dữ liệu danh mục từ mbw_ats: {str(e)}")
        frappe.log_error(frappe.get_traceback(), f"Lỗi xóa dữ liệu danh mục")
        return {
            "success": False,
            "message": f"Lỗi khi xóa dữ liệu danh mục: {str(e)}"
        }