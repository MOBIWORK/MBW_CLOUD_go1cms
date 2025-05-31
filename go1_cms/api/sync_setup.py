import frappe
from go1_cms.go1_cms.webhook.handler import fetch_linked_data

@frappe.whitelist()
def sync_from_external(doctype: str, identifiers: list[str] = None):
    """
    Đồng bộ dữ liệu từ hệ thống ngoài sau khi cài đặt (install).
    :param doctype: tên DocType cần đồng bộ (ví dụ: Customer, Item)
    :param identifiers: danh sách sync_id cụ thể để lấy (nếu có). Nếu không có sẽ lấy toàn bộ.
    """

    if not doctype:
        frappe.throw("Missing required parameter: doctype")

    synced = []
    failed = []

    if not identifiers:
        # Gọi hệ thống ngoài lấy toàn bộ sync_id để quét (tuỳ hệ thống ngoài hỗ trợ)
        identifiers = get_all_sync_ids_from_external(doctype)

    for sync_id in identifiers:
        try:
            fetch_linked_data(doctype, sync_id)
            synced.append(sync_id)
        except Exception as e:
            failed.append({ "sync_id": sync_id, "error": str(e) })

    return {
        "status": "completed",
        "synced_count": len(synced),
        "failed_count": len(failed),
        "synced": synced,
        "failed": failed
    }

def get_all_sync_ids_from_external(doctype: str) -> list:
    """
    Gọi hệ thống ngoài để lấy danh sách tất cả sync_id cần đồng bộ.
    API này phụ thuộc vào khả năng cung cấp phía hệ thống ngoài.
    """
    import requests
    from datetime import datetime, timedelta

    api_base = frappe.conf.get("ats_base_url")
    normalized_doctype = doctype.replace(" ", "_") 
    url = f"{api_base}/api/method/mbw_ats.integration.cms.{normalized_doctype}"
    api_token = frappe.conf.get("api_token")
    five_minutes_ago = datetime.now() - timedelta(minutes=6)
    timestamp_int = str(int(five_minutes_ago.timestamp()))
    headers={
        "Content-Type":"application/json",
        "x-authenication":f"Bearer {api_token}",
        "x-timestamp": timestamp_int
    }

    try:
        res = requests.post(url,json={}, headers=headers, timeout=5)
        res.raise_for_status()
        return res.json()  # giả định trả về list sync_id
    except Exception as e:
        frappe.throw(f"Lỗi lấy danh sách {doctype}: {str(e)}")
