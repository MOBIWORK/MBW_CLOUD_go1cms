# Copyright (c) 2025, mbwcloud.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ATS_Recruitment_Process(Document):
	pass

@frappe.whitelist()
def get_recruitment_process():
    """Lấy danh sách các vòng tuyển dụng từ ATS_Recruitment_Process, kèm trigger"""

    raw_rounds = frappe.get_all(
        "ATS_Recruitment_Process",
        fields=["name", "round_name", "round_type", "position", "default"],
        order_by="position asc"
    )

    # Nếu không có vòng nào
    if not raw_rounds:
        return {
            "fixedStart": [],
            "draggableRounds": [],
            "fixedEnd": [],
        }

    # Load từng vòng đầy đủ trigger
    rounds = []
    for r in raw_rounds:
        doc = frappe.get_doc("ATS_Recruitment_Process", r.name)
        r["triggers"] = [
            {
                "trigger_event": t.trigger_event,
                "action_type": t.action_type,
                "targets": t.targets,
                # "params": t.params or {},
                "enabled": t.enabled,
            }
            for t in doc.automation_rules
        ]
        rounds.append(r)

    # Nếu chỉ có 1 vòng, coi nó là vòng đầu tiên
    if len(rounds) == 1:
        return {
            "fixedStart": [rounds[0]],
            "draggableRounds": [],
            "fixedEnd": [],
        }

    # Nếu chỉ có 2 vòng, gán 1 vào fixedStart, 1 vào fixedEnd
    if len(rounds) == 2:
        return {
            "fixedStart": [rounds[0]],
            "draggableRounds": [],
            "fixedEnd": [rounds[1]],
        }

    # Nếu chỉ có 3 vòng, vòng đầu là fixedStart, 2 vòng còn lại là fixedEnd
    if len(rounds) == 3:
        return {
            "fixedStart": [rounds[0]],
            "draggableRounds": [],
            "fixedEnd": rounds[1:],  # 2 phần tử cuối
        }

    # Trường hợp bình thường: Chia danh sách thành 3 phần
    return {
        "fixedStart": [rounds[0]],  # Vòng đầu tiên
        "draggableRounds": rounds[1:-2],  # Các vòng có thể kéo thả (trừ 2 vòng cuối)
        "fixedEnd": rounds[-2:],  # 2 vòng cuối cùng
    }



@frappe.whitelist()
def update_round_positions(rounds_json):
    """
    Cập nhật vị trí của nhiều vòng tuyển dụng trong một lần gọi API
    """
    try:
        rounds = json.loads(rounds_json)  # Chuyển JSON thành danh sách
        for round in rounds:
            frappe.db.set_value("ATS_Recruitment_Process", round["name"], "position", round["position"])

        frappe.db.commit()  # Lưu thay đổi vào database
        return {"success": True, "message": "Positions updated successfully"}
    except Exception as e:
        frappe.log_error(f"Error updating recruitment process positions: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def delete_round(name):
    """
    Xóa vòng tuyển dụng và cập nhật lại vị trí các vòng sau nó.
    """
    try:
        # Lấy thông tin vòng bị xóa
        round_to_delete = frappe.get_doc("ATS_Recruitment_Process", name)
        position_to_remove = round_to_delete.position

        # Kiểm tra nếu vòng mặc định, không cho xóa
        if round_to_delete.default:
            return {"success": False, "message": "Cannot delete a default recruitment round."}

        # Xóa vòng
        frappe.delete_doc("ATS_Recruitment_Process", name)

        # Cập nhật lại vị trí cho các vòng phía sau
        rounds_to_update = frappe.get_all(
            "ATS_Recruitment_Process",
            filters={"position": [">", position_to_remove]},
            fields=["name", "position"],
            order_by="position ASC",
        )

        for round in rounds_to_update:
            frappe.db.set_value("ATS_Recruitment_Process", round.name, "position", round["position"] - 1)

        frappe.db.commit()
        return {"success": True, "message": "Recruitment round deleted successfully"}

    except Exception as e:
        frappe.log_error(f"Error deleting recruitment round: {str(e)}")
        return {"success": False, "message": str(e)}

import frappe
import json

@frappe.whitelist()
def update_end_round_positions_before_insert():
    """
    Cập nhật vị trí của 2 vòng cuối trước khi thêm một vòng mới.
    - Dời 2 vòng cuối xuống trước khi thêm vòng mới.
    """
    try:
        # Lấy danh sách 2 vòng cuối
        end_rounds = frappe.get_all(
            "ATS_Recruitment_Process",
            order_by="position DESC",
            fields=["name", "position"],
            limit=2  # Chỉ lấy 2 vòng cuối
        )

        if len(end_rounds) < 2:
            return {"success": False, "message": "Not enough rounds to update."}

        # Giữ nguyên vị trí vòng cuối cùng, chỉ dịch chuyển vòng áp chót
        new_positions = {
            end_rounds[1]["name"]: end_rounds[1]["position"] + 1,
            end_rounds[0]["name"]: end_rounds[0]["position"] + 1
        }

        for name, position in new_positions.items():
            frappe.db.set_value("ATS_Recruitment_Process", name, "position", position)

        frappe.db.commit()
        return {"success": True, "message": "End round positions updated successfully"}

    except Exception as e:
        frappe.log_error(f"Error updating end round positions: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_round_types_with_color():
    round_types = frappe.get_all(
        "ATS_Round_Type",
        fields=["name", "round_type_name", "color"],
        order_by="position asc"
    )

    # Chuyển đổi dữ liệu về dạng label, value, color
    formatted_round_types = [
        {
            "label": round.get("round_type_name"),  # Label hiển thị trên UI
            "value": round.get("name"),  # Value dùng để lưu trữ
            "color": round.get("color")  # Màu hiển thị
        }
        for round in round_types
    ]

    return {"message": formatted_round_types}

