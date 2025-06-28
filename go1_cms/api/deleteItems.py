import frappe
import json
from frappe import _

@frappe.whitelist()
def delete_items():
    """Xóa nhiều bản ghi, giữ lại những bản ghi không thể xóa và báo lỗi riêng."""
    items = sorted(json.loads(frappe.form_dict.get("items")), reverse=True)
    doctype = frappe.form_dict.get("doctype")

    if len(items) > 10:
        frappe.enqueue("frappe.desk.reportview.delete_bulk", doctype=doctype, items=items)
    else:
        return delete_bulk(doctype, items)  # Trả về phản hồi JSON


def delete_bulk(doctype, items):
    undeleted_items = []
    deleted_count = 0
    
    for i, d in enumerate(items):
        try:
            frappe.flags.in_bulk_delete = True
            frappe.delete_doc(doctype, d)

            deleted_count += 1  # Đếm số bản ghi xóa thành công

            if len(items) >= 5:
                frappe.publish_realtime(
                    "progress",
                    dict(
                        progress=[i + 1, len(items)],
                        title=_("Deleting {0}").format(doctype),
                        description=d,
                    ),
                    user=frappe.session.user,
                )

            # ✅ Chỉ commit những bản ghi xóa thành công
            frappe.db.commit()
        
        except Exception as e:
            # ❌ Nếu xóa thất bại, rollback CHỈ bản ghi đó, không ảnh hưởng đến các bản ghi khác
            undeleted_items.append({"item": d, "error": str(e)})
            frappe.db.rollback()

    # ✅ Nếu có bản ghi bị lỗi, trả về danh sách lỗi nhưng không rollback toàn bộ transaction
    return {
        "success": deleted_count > 0,
        "deleted_count": deleted_count,
        "errors": undeleted_items,
    }
