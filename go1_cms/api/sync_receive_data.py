import frappe
import json
from frappe import _

@frappe.whitelist()
def receive_category_data():
    """
    API endpoint để nhận dữ liệu danh mục từ mbw_ats
    """
    try:
        data = frappe.local.form_dict
        
        doctype = data.get('doctype')
        # Kiểm tra xem data có phải là dict hoặc str không và xử lý phù hợp
        if isinstance(data.get('data'), dict):
            item_data = frappe._dict(data.get('data'))
        else:
            item_data = frappe._dict(json.loads(data.get('data')))
            
        sync_field = data.get('sync_field', 'name')
        
        if not doctype or not item_data:
            return {
                "success": False,
                "message": "Thiếu thông tin doctype hoặc dữ liệu"
            }
            
        # Kiểm tra xem bản ghi đã tồn tại chưa
        sync_value = item_data.get(sync_field)
        existing_record = None
        
        if sync_value:
            # Tìm bản ghi dựa trên trường đồng bộ
            existing_docs = frappe.get_all(
                doctype,
                filters={sync_field: sync_value},
                fields=["name"]
            )
            
            if existing_docs:
                existing_record = existing_docs[0].name
        
        if existing_record:
            # Cập nhật bản ghi hiện có
            doc = frappe.get_doc(doctype, existing_record)
            
            # Cập nhật các trường
            for field, value in item_data.items():
                if frappe.get_meta(doctype).has_field(field):
                    setattr(doc, field, value)
                    
            # Đánh dấu để tránh đồng bộ ngược lại
            doc.flags.ignore_sync = True
            doc.sync_source = 1
            
            # Lưu bản ghi
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            return {
                "success": True,
                "message": f"Cập nhật thành công bản ghi {doctype}",
                "name": doc.name
            }
        else:
            # Tạo bản ghi mới
            doc = frappe.new_doc(doctype)
            
            # Thiết lập các trường từ dữ liệu
            for field, value in item_data.items():
                if frappe.get_meta(doctype).has_field(field):
                    setattr(doc, field, value)
            
            # Đánh dấu để tránh đồng bộ ngược lại
            doc.flags.ignore_sync = True
            doc.sync_source = 1
            
            # Lưu bản ghi
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            return {
                "success": True,
                "message": f"Tạo mới thành công bản ghi {doctype}",
                "name": doc.name
            }
    except Exception as e:
        frappe.logger("sync").error(f"Lỗi khi đồng bộ dữ liệu danh mục: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Lỗi đồng bộ dữ liệu danh mục")
        return {
            "success": False,
            "message": f"Lỗi khi đồng bộ dữ liệu danh mục: {str(e)}"
        }

@frappe.whitelist()
def delete_category_data():
    """
    API endpoint để xóa dữ liệu danh mục theo yêu cầu từ mbw_ats
    """
    try:
        data = frappe.local.form_dict
        
        doctype = data.get('doctype')
        name = data.get('name')
        sync_field = data.get('sync_field', 'name')
        
        if not doctype or not name:
            return {
                "success": False,
                "message": "Thiếu thông tin doctype hoặc name"
            }
            
        # Tìm bản ghi cần xóa
        existing_docs = frappe.get_all(
            doctype, 
            filters={sync_field: name},
            fields=["name"]
        )
        
        if not existing_docs:
            return {
                "success": True,
                "message": f"Không tìm thấy bản ghi {doctype} với {sync_field}={name} để xóa"
            }
            
        # Xóa bản ghi tìm thấy
        for doc_name in [d.name for d in existing_docs]:
            doc = frappe.get_doc(doctype, doc_name)
            
            # Đánh dấu để tránh đồng bộ ngược lại
            doc.flags.ignore_sync = True
            
            # Xóa bản ghi
            frappe.delete_doc(doctype, doc_name, ignore_permissions=True)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Đã xóa thành công {len(existing_docs)} bản ghi {doctype}"
        }
        
    except Exception as e:
        frappe.logger("sync").error(f"Lỗi khi xóa bản ghi danh mục: {str(e)}")
        frappe.log_error(frappe.get_traceback(), f"Lỗi khi xóa bản ghi {doctype}")
        return {
            "success": False,
            "message": f"Lỗi khi xóa bản ghi danh mục: {str(e)}"
        }