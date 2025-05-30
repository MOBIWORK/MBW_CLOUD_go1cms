import frappe
import hmac
import time
import hashlib
from functools import wraps

def secure_api():
    def decorator(func):
        @frappe.whitelist(allow_guest=True)
        @wraps(func)
        def wrapper(*args, **kwargs):
            headers = frappe._dict({k.lower(): v for k, v in frappe.request.headers.items()})
            max_age_seconds=300  # 5 phút
            # 1. Lấy token từ header
            received_token = headers.get("x-authenication", "").replace("Bearer ", "").strip()
            expected_token = frappe.conf.get("api_token")
            print(expected_token)

            if not received_token or received_token != expected_token:
                frappe.throw("Invalid or missing token", frappe.AuthenticationError)

            # 2. Lấy và kiểm tra timestamp
            try:
                received_timestamp = int(headers.get("x-timestamp"))
            except (TypeError, ValueError):
                frappe.throw("Invalid or missing timestamp")

            now = int(time.time())
            delta = abs(now - received_timestamp)

            # if delta > max_age_seconds:
            #     frappe.throw(f"Request expired (timestamp delta = {delta}s)")

            return func(*args, **kwargs)
        return wrapper
    return decorator

def secure_webhook(require_hmac=True, require_token=False):
    def decorator(func):
        @frappe.whitelist(allow_guest=True)  # 👈 Cho phép gọi từ bên ngoài
        @wraps(func)
        def wrapper(*args, **kwargs):
            headers = frappe._dict({k.lower(): v for k, v in frappe.request.headers.items()})
            
            # 1. HMAC signature (từ X-Signature)
            if require_hmac:
                secret = frappe.conf.get("webhook_secret", "default_secret")
                body = frappe.request.get_data(as_text=True)
                received_signature = headers.get("x-signature")

                if not received_signature:
                    frappe.throw("Missing HMAC signature")

                computed_signature = hmac.new(
                    key=secret.encode(),
                    msg=body.encode(),
                    digestmod=hashlib.sha256
                ).hexdigest()

                if not hmac.compare_digest(computed_signature, received_signature):
                    frappe.throw("Invalid HMAC signature")

            # 2. Token header (Authorization: Bearer <token>)
            if require_token:
                expected_token = frappe.conf.get("api_token")
                received_token = headers.get("x-authorization", "").replace("Bearer ", "")

                if not received_token or received_token != expected_token:
                    frappe.throw("Invalid or missing token")

            return func(*args, **kwargs)
        return wrapper
    return decorator