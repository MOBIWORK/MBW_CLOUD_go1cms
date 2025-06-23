import os
import string
import random
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import frappe
from frappe import _, local
from frappe.utils import now, add_to_date


@frappe.whitelist(methods=['GET'], allow_guest=True)
def get_captcha():
    # CAPTCHA config
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    width, height = 300, 100
    background_color = (255, 255, 255)
    text_color = (0, 0, 0)

    # Font settings
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Tùy hệ thống
    font_size = 48
    if not os.path.exists(font_path):
        return {"error": "Font not found at " + font_path}
    
    font = ImageFont.truetype(font_path, font_size)

    # Tạo ảnh trắng
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Tính toán vị trí từng ký tự để giãn cách đều
    spacing = (width - 40) // len(captcha_text)  # khoảng cách ký tự
    start_x = 20
    y = (height - font_size) // 2

    for i, char in enumerate(captcha_text):
        x = start_x + i * spacing
        draw.text((x, y), char, font=font, fill=text_color)

    # Encode base64
    data = BytesIO()
    image.save(data, format='PNG')
    data.seek(0)
    image_base64 = base64.b64encode(data.getvalue()).decode('utf-8')

    ip = local.request.remote_addr

    # Xóa captcha cũ
    old_datetime = add_to_date(now(), minutes=-10)
    frappe.db.delete("CMS Captcha", {
        "creation": ("<", old_datetime),
        "ip": ip
    })

    # Lưu mới
    new_doc = frappe.new_doc('CMS Captcha')
    new_doc.ip = ip
    new_doc.captcha_text = captcha_text
    new_doc.captcha_image = image_base64
    new_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        'captcha_image': "data:image/png;base64," + image_base64,
    }
