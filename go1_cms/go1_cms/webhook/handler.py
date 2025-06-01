
import frappe
import requests
from frappe.exceptions import ValidationError, DoesNotExistError
from go1_cms.utlis.webhook_utils import log_webhook_result
from datetime import datetime, timedelta

def parse_webhook_data(data: dict, doctype: str, key_field: str = "sync_id"):
    action = data.get("action", "insert").lower()
    sync_key = data.get(key_field)

    if not sync_key:
        frappe.throw(f"Missing key field '{key_field}' in webhook payload")

    # Đồng bộ các trường Link nếu thiếu
    sync_linked_documents(data, doctype)

    # Kiểm tra tồn tại bản ghi
    existing = frappe.get_all(doctype, filters={key_field: sync_key}, limit=1)
    exists = bool(existing)
    docname = existing[0].name if exists else None

    # Lấy metadata để xác định các field không nên update
    meta = frappe.get_meta(doctype)
    skip_fieldtypes = {'Section Break', 'Column Break', 'Button', 'HTML', 'Table of Contents'}
    skip_fieldnames = {'name', 'owner', 'creation', 'modified', 'modified_by', 'doctype'}

    non_updatable_fields = {
        df.fieldname for df in meta.fields
        if df.read_only or df.unique or df.fieldtype in skip_fieldtypes or df.fieldname in skip_fieldnames
    }

    if action == "insert":
        if exists:
            frappe.throw(f"Record with {key_field} '{sync_key}' already exists")
        doc = frappe.get_doc({ "doctype": doctype, **data })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        log_webhook_result(doctype, sync_key, "insert", "success", "Inserted", data)
    elif action == "update":
        if not exists:
            # fallback to insert
            doc = frappe.get_doc({ "doctype": doctype, **data })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            log_webhook_result(doctype, sync_key, "insert", "success", "Inserted", data)
        else:
            safe_save(non_updatable_fields, data, doctype, docname)
            log_webhook_result(doctype, sync_key, "update", "success", f"Updated field(s)", data)

    elif action == "delete":
        if not exists:
            frappe.throw(f"Record with {key_field} '{sync_key}' does not exist")
        frappe.delete_doc(doctype, docname, ignore_permissions=True)
        frappe.db.commit()
        log_webhook_result(doctype, sync_key, "delete", "success", "Deleted", data)
    else:
        frappe.throw(f"Unsupported action: {action}")

def parse_webhook_data_batch(payload: dict, key_field: str = "sync_id"):
    """
    Xử lý batch webhook data:
    - Kiểm tra sync_id
    - Đồng bộ link liên kết
    - Thực hiện insert/update/delete
    - Ghi log kết quả từng bản ghi
    """
    doctype = payload.get("doctype")
    records = payload.get("records", [])

    if not doctype or not records:
        frappe.throw("Missing 'doctype' or 'records' in payload")

    results = []
    meta = frappe.get_meta(doctype)

    # Các field không được update
    skip_fieldtypes = {'Section Break', 'Column Break', 'Button', 'HTML', 'Table of Contents'}
    skip_fieldnames = {'name', 'owner', 'creation', 'modified', 'modified_by', 'doctype'}
    non_updatable_fields = {
        df.fieldname
        for df in meta.fields
        if df.read_only or df.unique or df.fieldtype in skip_fieldtypes or df.fieldname in skip_fieldnames
    }

    for data in records:
        sync_key = data.get(key_field)
        action = data.get("action", "insert").lower()

        if not sync_key:
            results.append({ "status": "error", "message": f"Missing '{key_field}'", "data": data })
            continue

        try:
            sync_linked_documents(data, doctype)
        except Exception as sync_err:
            log_webhook_result(doctype, sync_key, action, "error", f"Link sync failed: {sync_err}", data)
            results.append({ "status": "error", "action": action, "sync_id": sync_key, "message": str(sync_err) })
            continue

        existing = frappe.get_all(doctype, filters={key_field: sync_key}, limit=1)
        exists = bool(existing)
        docname = existing[0].name if exists else None

        try:
            if action == "insert":
                if exists:
                    raise frappe.ValidationError(f"Record with {key_field} '{sync_key}' already exists")
                doc = frappe.get_doc({ "doctype": doctype, **data })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
                log_webhook_result(doctype, sync_key, "insert", "success", "Inserted", data)
                results.append({ "status": "success", "action": "insert", "sync_id": sync_key })

            elif action == "update":
                if not exists:
                    doc = frappe.get_doc({ "doctype": doctype, **data })
                    doc.insert(ignore_permissions=True)
                    frappe.db.commit()
                    log_webhook_result(doctype, sync_key, "insert", "success", "Auto-inserted via update", data)
                    results.append({ "status": "success", "action": "insert (via update)", "sync_id": sync_key })
                else:
                    safe_save(non_updatable_fields, data, doctype, sync_key)
                    log_webhook_result(doctype, sync_key, "update", "success", f"Updated field(s)", data)
                    results.append({ "status": "success", "action": "update", "sync_id": sync_key })

            elif action == "delete":
                if not exists:
                    raise frappe.ValidationError(f"Record with {key_field} '{sync_key}' does not exist")
                frappe.delete_doc(doctype, docname, ignore_permissions=True)
                frappe.db.commit()
                log_webhook_result(doctype, sync_key, "delete", "success", "Deleted", data)
                results.append({ "status": "success", "action": "delete", "sync_id": sync_key })

            else:
                raise frappe.ValidationError(f"Unsupported action: {action}")

        except Exception as e:
            print(frappe.get_traceback())
            log_webhook_result(doctype, sync_key, action, "error", str(e), data)
            results.append({ "status": "error", "action": action, "sync_id": sync_key, "message": str(e) })

    return results

def handle_doc_event(doc, method):
    """
    Event hook xử lý CRUD cho DocType thông qua các sự kiện của Frappe
    """
    action_map = {
        "after_insert": "insert",
        "on_update": "update",
        "on_trash": "delete"
    }

    action = action_map.get(method)
    if not action:
        return

    # Chuyển Doc thành dict
    doc_data = doc.as_dict()
    doc_data["action"] = action
    doc_data["doctype"] = doc.doctype

    # Log để kiểm tra (tuỳ chọn)
    frappe.logger("Webhook").info(f"[EVENT] {action.upper()} - {doc.doctype} - {doc.name}")

    parse_webhook_data(doc_data, doc.doctype) 

def sync_linked_documents(data: dict, parent_doctype: str):
    """
    Tự động duyệt các trường Link trong DocType, kiểm tra nếu bản ghi chưa tồn tại thì gọi API ngoài
    để lấy dữ liệu và insert/update bản ghi tham chiếu.
    """

    meta = frappe.get_meta(parent_doctype)
    link_fields = [df for df in meta.fields if df.fieldtype == "Link"]

    for df in link_fields:
        fieldname = df.fieldname
        target_doctype = df.options  # ví dụ: "Customer", "Item"
        ref_value = data.get(fieldname)

        if not ref_value or not target_doctype:
            continue

        # Bỏ qua nếu đã tồn tại
        if frappe.db.exists(target_doctype, ref_value):
            continue

        # Gọi hệ thống ngoài để fetch + xử lý insert/update theo sync_id
        try:
            frappe.logger("Webhook").info(f"Syncing missing linked {target_doctype}: {ref_value}")
            fetch_linked_data(target_doctype, ref_value)
        except Exception as e:
            frappe.log_error(
                f"Lỗi khi đồng bộ {target_doctype} với {fieldname} = {ref_value}: {e}",
                "sync_linked_documents"
            )

def fetch_linked_data(doctype: str, identifier: str):
    api_base = frappe.conf.get("ats_base_url")
    normalized_doctype = doctype.replace(" ", "_") 
    url = f"{api_base}/api/method/mbw_ats.integration.cms.{normalized_doctype}"
    api_token = frappe.conf.get("api_token")
    five_minutes_ago = datetime.now() - timedelta(minutes=6)
    timestamp_int = str(int(five_minutes_ago.timestamp()))
    headers={
        "x-authenication":f"Bearer {api_token}",
        "x-timestamp": timestamp_int
    }
    try:
        res = requests.post(url, json={ "sync_id": identifier },headers=headers, timeout=5)
        res.raise_for_status()
        
        records = res.json().get("message")
        if not isinstance(records, list):
            records = [records]  # nếu chỉ trả về 1 bản ghi
        print(f"Response from {url}: {records}")
        for record in records:
            sync_id = record.get("sync_id")
            if not sync_id:
                frappe.log_error(f"Missing sync_id in linked data for {doctype}", "Linked Sync Error")
                continue

            existing = frappe.get_all(doctype, filters={ "sync_id": sync_id }, limit=1)
            if existing:
                continue
                # Update
                # doc = frappe.get_doc(doctype, existing[0].name)
                # for key, value in record.items():
                #     if key not in ["doctype", "name"] and hasattr(doc, key):
                #         setattr(doc, key, value)
                # doc.save(ignore_permissions=True)
                # frappe.logger("Webhook").info(f"Updated linked {doctype} ({sync_id})")
            else:
                # Insert
                doc = frappe.get_doc({ "doctype": doctype, **record })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.logger("Webhook").info(f"Inserted linked {doctype} ({sync_id})")

        

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"fetch_linked_data: {doctype} ({identifier})")

def safe_save(non_updatable_fields, data, doctype, sync_key):
    frappe.db.rollback()  #    
    
    fresh_doc = frappe.get_doc(doctype, {"sync_id": sync_key})
  
    for key, value in data.items():
        if key in non_updatable_fields or not hasattr(fresh_doc, key):
            continue
        if getattr(fresh_doc, key) != value:
            frappe.db.set_value(doctype, {"sync_id": sync_key}, key, value, update_modified=False)
    frappe.db.commit()