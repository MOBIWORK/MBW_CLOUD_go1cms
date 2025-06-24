# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import json
import re
import frappe
from frappe import _, safe_decode
from frappe.model.document import Document
from frappe.utils import cstr, comma_and, cint, get_url
from fuzzywuzzy import fuzz
import unicodedata
# from lms.lms.doctype.course_lesson.course_lesson import save_progress
# from lms.lms.utils import (
# 	generate_slug,
# 	has_course_moderator_role,
# 	has_course_instructor_role,
# )
from binascii import Error as BinasciiError
from frappe.utils.file_manager import safe_b64decode
from frappe.core.doctype.file.utils import get_random_filename
import html
# from mbw_ats.api.mail import send_email

from frappe import request

class LMSQuiz(Document):
	pass