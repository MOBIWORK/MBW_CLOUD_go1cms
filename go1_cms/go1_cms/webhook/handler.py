
import frappe
import requests
import json
from frappe.exceptions import ValidationError, DoesNotExistError

from go1_cms.utlis.webhook_utils import log_webhook_result
from datetime import datetime, timedelta
from frappe.utils import nowdate, now_datetime
import uuid

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
    skip_fieldtypes = {'Section Break', 'Column Break', 'Button'}
    skip_fieldnames = {'name', 'owner', 'sync_id','creation', 'modified', 'modified_by', 'doctype'}

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
        frappe.flags.ignore_webhook_sync = True
        log_webhook_result(doctype, sync_key, "insert", "success", "Inserted", data)
    elif action == "update":
        if not exists:
            # fallback to insert
            doc = frappe.get_doc({ "doctype": doctype, **data })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.flags.ignore_webhook_sync = True
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

    #Kiểm tra lấy danh mục trước khi sync lần đầu
    if not check_exists_cate():
        sync_from_ats()
    
    # Các field không được update
    skip_fieldtypes = {'Section Break', 'Column Break', 'Button'}
    skip_fieldnames = {'name', 'owner','can_id', 'sync_id','creation', 'modified', 'modified_by', 'doctype'}
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
                frappe.flags.ignore_webhook_sync = True
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
                log_webhook_result(doctype, sync_key, "insert", "success", "Inserted", data)
                results.append({ "status": "success", "action": "insert", "sync_id": sync_key })

            elif action == "update":
                if not exists:
                    doc = frappe.get_doc({ "doctype": doctype, **data })
                    frappe.flags.ignore_webhook_sync = True
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
    action_map = {"after_insert": "insert", "on_update": "update", "on_trash": "delete"}
    action = action_map.get(method)
    if not action:
        return

    # Đảm bảo doc có sync_id
    if not getattr(doc, "sync_id", None):
        new_sync_id = str(uuid.uuid4())
        doc.db_set("sync_id", new_sync_id)
        doc.sync_id = new_sync_id
    
    # Print debug info sau khi đã xử lý sync_id
    print("Nhận hook",getattr(frappe.flags, "ignore_webhook_sync", False), doc.sync_id, doc.doctype)
    print("co chay nhe ban nhe")
    
    #Kiểm tra xem có can_application_date (chỉ áp dụng cho ATS_Candidate)
    if doc.doctype == "ATS_Candidate" and not getattr(doc, "can_application_date", None):
        can_application_date_new = nowdate()
        doc.db_set("can_application_date", can_application_date_new)
        doc.can_application_date = can_application_date_new

    if (getattr(frappe.flags, "ignore_webhook_sync", True) or not doc.sync_id):
        frappe.logger("Webhook").info(
            f"[SKIP] Insert event for {doc.doctype} {doc.name} due to ignore_sync flag"
        )
        frappe.flags.ignore_webhook_sync = False       
        return

    # Tạo payload
    raw_record = doc.as_dict()
    raw_record["action"] = action
    payload = {"doctype": doc.doctype, "records": [{**raw_record, "action": action}]}
    
    # Gửi webhook
    frappe.enqueue(
        "go1_cms.utlis.webhook_utils.forward_webhook",
        queue="short",
        timeout=300,
        now=True,
        doc_data=payload,
    )

    frappe.logger("Webhook").info(
        f"[EVENT] {action.upper()} - {doc.doctype} - {doc.name}"
    )

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
    api_base = frappe.conf.get("webhook_base_url")
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
    
    frappe.db.rollback()
    fresh_doc = frappe.get_doc(doctype, {"sync_id": sync_key})
    meta = frappe.get_meta(doctype)

    for key, value in data.items():
        if key in non_updatable_fields or not hasattr(fresh_doc, key):
            continue

        field_meta = meta.get_field(key)
        if not field_meta:
            continue

        fieldtype = field_meta.fieldtype

        # Trường kiểu Table
        if fieldtype == "Table" and isinstance(value, list):
            child_doctype = field_meta.options
            existing = [row.as_dict() for row in fresh_doc.get(key)]

            if existing != value:
                fresh_doc.set(key, [])
                for row in value:
                    row.pop("name", None)  # Xoá name để tránh trùng key
                    child_doc = frappe.new_doc(child_doctype)
                    child_doc.update(row)
                    fresh_doc.append(key, child_doc)

        # Trường kiểu Table MultiSelect
        elif fieldtype == "Table MultiSelect" and isinstance(value, list):
            # Normalize danh sách link hiện có
            existing_links = sorted([d.link for d in fresh_doc.get(key)])
            incoming_links = sorted([d.get("link") for d in value if d.get("link")])

            if existing_links != incoming_links:
                fresh_doc.set(key, [])
                for row in value:
                    row.pop("name", None)  # Xoá name để tránh trùng key
                    if row.get("link"):
                        fresh_doc.append(key, {"link": row["link"]})

        # Trường kiểu dict/list nhưng được lưu dưới dạng text
        elif isinstance(value, (list, dict)) and fieldtype in ["Data", "Small Text", "Text", "Code"]:
            value_json = json.dumps(value)
            current_value = getattr(fresh_doc, key)
            if current_value != value_json:
                setattr(fresh_doc, key, value_json)

        # Trường Check (bool/int 0/1)
        elif fieldtype == "Check":
            normalized_new = 1 if value in (1, "1", True, "true", "True") else 0
            normalized_current = 1 if getattr(fresh_doc, key) in (1, "1", True, "true", "True") else 0

            if normalized_new != normalized_current:
                setattr(fresh_doc, key, normalized_new)

        # Trường primitive thông thường
        elif not isinstance(value, (list, dict)):
            if getattr(fresh_doc, key) != value:
                setattr(fresh_doc, key, value)
    frappe.flags.ignore_webhook_sync = True
    fresh_doc.save(ignore_permissions=True)
    frappe.db.commit()
    
def check_exists_cate():
    total_location = frappe.db.count("ATS_Location")
    total_position = frappe.db.count("ATS_Position")
    if total_location > 0 and total_position > 0:
        return True
    else:
        return False

def sync_from_ats():
    from go1_cms.api.sync_setup import sync_from_external
    try:
        sync_from_external("ATS_Country")
        sync_from_external("ATS_Province")
        sync_from_external("ATS_District")
        sync_from_external("ATS_Ward")        
        sync_from_external("ATS_Company")
        sync_from_external("ATS_Unit")
        sync_from_external("ATS_Profession")
        sync_from_external("ATS_Level")
        sync_from_external("ATS_Location")     
        sync_from_external("ATS_EducationLevel")
        sync_from_external("ATS_Education")
        sync_from_external("ATS_Institution")
        sync_from_external("ATS_Major")
        sync_from_external("ATS_Round_Type")
        sync_from_external("ATS_Recruitment_Process")     
        sync_from_external("ATS_Position")   
        sync_from_external("ATS_CandidateSource")
        sync_from_external("ATS_RejectReasonCampaignGroup")
        sync_from_external("Hiring Committee")
        sync_from_external("Hiring_Committee_Schedule")
        sync_from_external("Job_Opening_Rounds")
        sync_from_external("Job_Position_Rounds")
        sync_from_external("Candidate_Award")
        sync_from_external("Candidate_Certification")
        sync_from_external("Candidate_Project")
        sync_from_external("Candidate_Course")
        sync_from_external("Candidate_Skill")
        sync_from_external("Candidate_Work_Experience")
        sync_from_external("ATS_CandidateRoundHistory")
        sync_from_external("Candidate Stages")
        sync_from_external("ATS_JobOpening")

    except Exception as e:
        frappe.log_error("Error sync from get ", frappe.get_traceback())