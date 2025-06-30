# Copyright (c) 2025, Tridotstech and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class ATS_Round_Type(Document):
	pass

@frappe.whitelist()
def get_round_types():
    """Lấy danh sách các vòng tuyển dụng từ ATS_Round_Type"""
    rounds = frappe.get_all(
        "ATS_Round_Type",
        fields=["name", "round_type_name", "color", "position", "default"],
        order_by="position asc"
    )

    if len(rounds) < 2:
        return {
            "fixedStart": rounds[:1],  # Chỉ có vòng đầu
            "draggableRounds": [],
            "fixedEnd": rounds[1:],  # Nếu chỉ có 2 phần tử, thì vòng còn lại là vòng cuối
        }

    return {
        "fixedStart": [rounds[0]],  # Chỉ có vòng đầu
        "draggableRounds": rounds[1:-1],  # Chỉ có các vòng ở giữa (có thể kéo thả)
        "fixedEnd": [rounds[-1]],  # Chỉ có vòng cuối
    }

@frappe.whitelist()
def update_round_positions(rounds_json):
    """
    Cập nhật vị trí của nhiều vòng tuyển dụng trong một lần gọi API
    """
    try:
        rounds = json.loads(rounds_json)  # Chuyển JSON thành list
        for round in rounds:
            frappe.db.set_value("ATS_Round_Type", round["name"], "position", round["position"])

        frappe.db.commit()  # Lưu thay đổi vào database
        return {"success": True, "message": "Positions updated successfully"}
    except Exception as e:
        frappe.log_error(f"Error updating round positions: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def delete_round(name):
    """
    Xóa vòng tuyển dụng và cập nhật lại vị trí các vòng sau nó.
    """
    try:
        # Lấy thông tin vòng bị xóa
        round_to_delete = frappe.get_doc("ATS_Round_Type", name)
        position_to_remove = round_to_delete.position

        # Kiểm tra nếu vòng mặc định, không cho xóa
        if round_to_delete.default:
            return {"success": False, "message": "Cannot delete default round."}

        # Xóa vòng
        frappe.delete_doc("ATS_Round_Type", name)

        # Cập nhật lại vị trí cho các vòng phía sau
        rounds_to_update = frappe.get_all(
            "ATS_Round_Type",
            filters={"position": [">", position_to_remove]},
            fields=["name", "position"],
            order_by="position ASC",
        )

        for round in rounds_to_update:
            frappe.db.set_value("ATS_Round_Type", round.name, "position", round["position"] - 1)

        frappe.db.commit()
        return {"success": True, "message": "Round deleted successfully"}

    except Exception as e:
        frappe.log_error(f"Error deleting round: {str(e)}")
        return {"success": False, "message": str(e)}

