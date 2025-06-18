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
from mbw_ats.api.mail import send_email

from frappe import request

class LMSQuiz(Document):
	def validate(self):
		self.validate_duplicate_questions()
		self.validate_limit()
		self.calculate_total_marks()
		self.validate_open_ended_questions()

	def validate_duplicate_questions(self):
		questions = [row.question for row in self.questions]
		rows = [i + 1 for i, x in enumerate(questions) if questions.count(x) > 1]
		if len(rows):
			frappe.throw(
				_("Rows {0} have the duplicate questions.").format(frappe.bold(comma_and(rows)))
			)

	def validate_limit(self):
		if self.limit_questions_to and cint(self.limit_questions_to) >= len(self.questions):
			frappe.throw(
				_("Limit cannot be greater than or equal to the number of questions in the quiz.")
			)

		if self.limit_questions_to and cint(self.limit_questions_to) < len(self.questions):
			marks = [question.marks for question in self.questions]
			if len(set(marks)) > 1:
				frappe.throw(_("All questions should have the same marks if the limit is set."))

	def calculate_total_marks(self):
		if self.limit_questions_to:
			self.total_marks = sum(
				question.marks for question in self.questions[: cint(self.limit_questions_to)]
			)
		else:
			self.total_marks = sum(cint(question.marks) for question in self.questions)

	def validate_open_ended_questions(self):
		types = [question.type for question in self.questions]
		types = set(types)

		if "Open Ended" in types:
			if len(types) > 1:
				frappe.throw(
					_(
						"If you want open ended questions then make sure each question in the quiz is of open ended type."
					)
				)
			else:
				self.show_answers = 0

	def autoname(self):
		pass
		# if not self.name:
		# 	self.name = generate_slug(self.title, "LMS Quiz")

	def get_last_submission_details(self):
		"""Returns the latest submission for this user."""
		user = frappe.session.user
		if not user or user == "Guest":
			return

		result = frappe.get_all(
			"LMS Quiz Submission",
			fields="*",
			filters={"owner": user, "quiz": self.name},
			order_by="creation desc",
			page_length=1,
		)

		if result:
			return result[0]



def clean_text(text):
    # Hạ thấp chữ
    text = text.lower()
    # Loại bỏ dấu tiếng Việt (nếu muốn so sánh không dấu)
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    # Xóa ký tự đặc biệt và khoảng trắng thừa
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
def set_total_marks(questions):
	marks = 0
	for question in questions:
		marks += question.get("marks")
	return marks


@frappe.whitelist(allow_guest=True)
def quiz_summary(quiz, results, member_email=None):
	score = 0
	results = results and json.loads(results)
	is_open_ended = False
	percentage = 0
	is_knocked_out = False
	knockout_question = None

	quiz_details = frappe.db.get_value(
		"LMS Quiz",
		quiz,
		["total_marks", "passing_percentage", "job_opening_id", "title", "max_attempts"],
		as_dict=1,
	)

	# Kiểm tra giới hạn số lần làm bài
	if quiz_details.get("max_attempts"):
		current_user = frappe.session.user
		
		# Tạo các điều kiện lọc dựa trên loại người dùng
		filters = {"quiz": quiz}
		
		if current_user == "Guest" or member_email:
			if member_email:
				# Nếu là người dùng khách hoặc có email được cung cấp, tìm theo member_candidate
				filters["member_candidate"] = member_email
		else:
			# Nếu là người dùng đã đăng nhập, tìm theo member
			filters["member"] = current_user
		
		# Đếm số lần làm bài của người dùng này
		attempt_count = frappe.db.count("LMS Quiz Submission", filters=filters)
		
		if attempt_count >= quiz_details.max_attempts:
			frappe.throw(
				_("Bạn đã vượt quá số lần làm bài cho phép ({0}).").format(
					quiz_details.max_attempts
				),
				title=_("Maximum Attempts Exceeded"),
				exc=frappe.exceptions.ValidationError
			)

	score_out_of = quiz_details.total_marks

	for result in results:
		question_name = result["question_name"]
		
		# Use the proper get_question_details function from utils.py that handles knockout priority logic
		from mbw_ats.mbw_ats.utils import get_question_details
		question_details = get_question_details(question_name)
		
		# If question details not found, skip this result
		if not question_details:
			frappe.log_error(f"Question details not found for question_name: {question_name} in quiz: {quiz}")
			continue

		# Extract the linked LMS Question ID for question_name field
		linked_question_id = question_details.get("quiz_question_name", question_name)
		if frappe.db.exists("LMS Quiz Question", question_name):
			linked_lms_question = frappe.db.get_value("LMS Quiz Question", question_name, "question")
			if linked_lms_question:
				linked_question_id = linked_lms_question

		result["question_name"] = linked_question_id
		result["question"] = question_details.get("question", "")
		result["marks_out_of"] = question_details.get("marks", 1)

		if question_details.get("type") != "Open Ended":
			correct = result["is_correct"][0]
			for point in result["is_correct"]:
				correct = correct and point
			result["is_correct"] = correct

			# Check for knockout question FIRST using the proper knockout logic
			if question_details.get("is_knockout") and not correct:
				is_knocked_out = True
				knockout_question = question_details.get("question", "")
				result["marks"] = 0
				# Dừng ngay lập tức khi knockout
				break
			else:
				marks = question_details.get("marks", 1) if correct else 0
				result["marks"] = marks
				score += marks

		else:
			result["is_correct"] = 0
			is_open_ended = True

		percentage = (score / score_out_of) * 100
		result["answer"] = re.sub(
			r'<img[^>]*src\s*=\s*["\'](?=data:)(.*?)["\']', _save_file, result["answer"]
			)

	# If knocked out, set score and percentage to 0
	if is_knocked_out:
		score = 0
		percentage = 0

	# Lấy thông tin người dùng hiện tại
	current_user = frappe.session.user
	
	# Tạo bài nộp mới
	submission = frappe.new_doc("LMS Quiz Submission")
	
	# Kiểm tra các trường tồn tại trong doctype
	meta = frappe.get_meta("LMS Quiz Submission")
	doc_fields = [field.fieldname for field in meta.fields]
	
	# Tạo data để insert
	submission_data = {
		"doctype": "LMS Quiz Submission",
		"quiz": quiz,
		"score": score,
		"score_out_of": score_out_of,
		"member": current_user if current_user != "Guest" else "Guest",
		"percentage": percentage,
		"passing_percentage": quiz_details.passing_percentage,
		"job_opening_id": quiz_details.job_opening_id,
		"quiz_title": quiz_details.title,
		"is_knocked_out": is_knocked_out,
		"knockout_question": knockout_question
	}
	
	# Thêm member_email nếu trường tồn tại
	if "member_email" in doc_fields and member_email:
		submission_data["member_email"] = member_email
	
	# Thêm member_candidate nếu trường tồn tại
	if "member_candidate" in doc_fields and member_email:
		submission_data["member_candidate"] = member_email
	
	# Cập nhật submission từng field một để tránh lỗi với serialized data
	for key, value in submission_data.items():
		if key != "doctype":  # Bỏ qua doctype vì đã được set
			submission.set(key, value)
	
	# Thêm results vào child table
	if results:
		for result in results:
			quiz_result = submission.append("result", {})
			quiz_result.question = result.get("question", "")
			
			# Ensure question_name contains the correct LMS Question ID, not LMS Quiz Question ID
			question_name_value = result.get("question_name", "")
			
			# If question_name is an LMS Quiz Question ID, get the linked LMS Question ID
			if question_name_value and frappe.db.exists("LMS Quiz Question", question_name_value):
				linked_question = frappe.db.get_value("LMS Quiz Question", question_name_value, "question")
				if linked_question and frappe.db.exists("LMS Question", linked_question):
					question_name_value = linked_question
				else:
					# If no valid linked question, leave empty to avoid validation error
					question_name_value = ""
			elif question_name_value and not frappe.db.exists("LMS Question", question_name_value):
				# If it's not a valid LMS Question ID, leave empty to avoid validation error
				question_name_value = ""
			
			quiz_result.question_name = question_name_value
			quiz_result.answer = result.get("answer", "")
			quiz_result.marks = result.get("marks", 0)
			quiz_result.marks_out_of = result.get("marks_out_of", 0)
			quiz_result.is_correct = 1 if result.get("is_correct") else 0
	
	# Lưu bài nộp
	submission.insert(ignore_permissions=True)
	frappe.db.commit()  # Đảm bảo lưu dữ liệu ngay lập tức
	
	if member_email and quiz_details.job_opening_id:
		update_result = update_candidate_quiz_results(member_email, quiz_details.job_opening_id, submission.name)
		print(f"Cập nhật kết quả cho ứng viên: {update_result}")
	

	return {
		"score": score,
		"score_out_of": score_out_of,
		"submission": submission.name,
		"pass": percentage >= quiz_details.passing_percentage and not is_knocked_out,
		"percentage": percentage,
		"is_open_ended": is_open_ended,
		"is_knocked_out": is_knocked_out,
		"knockout_question": knockout_question,
	}


def _save_file(match):
	data = match.group(1).split("data:")[1]
	headers, content = data.split(",")
	mtype = headers.split(";", 1)[0]

	if isinstance(content, str):
		content = content.encode("utf-8")
	if b"," in content:
		content = content.split(b",")[1]

	try:
		content = safe_b64decode(content)
	except BinasciiError:
		frappe.flags.has_dataurl = True
		return f'<img src="#broken-image" alt="{get_corrupted_image_msg()}"'

	if "filename=" in headers:
		filename = headers.split("filename=")[-1]
		filename = safe_decode(filename).split(";", 1)[0]

	else:
		filename = get_random_filename(content_type=mtype)

	_file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": filename,
			"content": content,
			"decode": False,
			"is_private": False,
		}
	)
	_file.save(ignore_permissions=True)
	file_url = _file.unique_url
	frappe.flags.has_dataurl = True

	return f'<img src="{file_url}"'


def get_corrupted_image_msg():
	return _("Image: Corrupted Data Stream")


@frappe.whitelist()
def get_question_details(question):
	if not question:
		return None
		
	if frappe.db.exists("LMS Quiz Question", question):
		fields = ["name", "question", "type"]
		for num in range(1, 5):
			fields.append(f"option_{cstr(num)}")
			fields.append(f"is_correct_{cstr(num)}")
			fields.append(f"explanation_{cstr(num)}")
			fields.append(f"possibility_{cstr(num)}")

		result = frappe.db.get_value("LMS Quiz Question", question, fields, as_dict=1)
		return result if result else None
	return None


@frappe.whitelist(allow_guest=True)
def check_answer(question, type, answers):
	try:
		# Kiểm tra tham số đầu vào
		if not question:
			frappe.throw(_("Question parameter is required"))
		
		if not type:
			frappe.throw(_("Type parameter is required"))
		
		if not answers:
			frappe.throw(_("Answers parameter is required"))
		
		# Parse JSON answers
		if isinstance(answers, str):
			answers = json.loads(answers)
		
		# Kiểm tra answers là list
		if not isinstance(answers, list):
			frappe.throw(_("Answers must be a list"))
		
		if type == "Choices":
			return check_choice_answers(question, answers)
		else:
			# Kiểm tra có ít nhất 1 answer cho User Input
			if len(answers) == 0:
				frappe.throw(_("At least one answer is required for User Input questions"))
			return check_input_answers(question, answers[0])
			
	except json.JSONDecodeError:
		frappe.throw(_("Invalid JSON format for answers"))
	except Exception as e:
		frappe.log_error(f"Error in check_answer: {str(e)}")
		frappe.throw(_("Error checking answer: {0}").format(str(e)))


def resolve_question_id(question_id):
	"""
	Resolve the actual LMS Question ID from either LMS Question or LMS Quiz Question ID
	
	Args:
		question_id: Could be either LMS Question ID or LMS Quiz Question ID
		
	Returns:
		str: The actual LMS Question ID to use for getting question details
	"""
	# First check if it's directly an LMS Question
	if frappe.db.exists("LMS Question", question_id):
		return question_id
	
	# If not, check if it's an LMS Quiz Question and get the linked question
	if frappe.db.exists("LMS Quiz Question", question_id):
		linked_question = frappe.db.get_value("LMS Quiz Question", question_id, "question")
		if linked_question and frappe.db.exists("LMS Question", linked_question):
			return linked_question
		else:
			frappe.throw(_("LMS Quiz Question {0} does not have a valid linked LMS Question").format(question_id))
	
	# If neither exists, throw error
	frappe.throw(_("Question not found: {0}").format(question_id))


def check_choice_answers(question, answers):
	# Resolve the actual LMS Question ID
	actual_question_id = resolve_question_id(question)
	
	fields = ["multiple"]
	is_correct = []
	for num in range(1, 5):
		fields.append(f"option_{cstr(num)}")
		fields.append(f"is_correct_{cstr(num)}")

	question_details = frappe.db.get_value("LMS Question", actual_question_id, fields, as_dict=1)
	
	# Kiểm tra nếu question_details là None
	if not question_details:
		frappe.throw(_("Question not found: {0}").format(actual_question_id))

	for num in range(1, 5):
		option_key = f"option_{num}"
		is_correct_key = f"is_correct_{num}"
		
		# Kiểm tra an toàn trước khi truy cập
		option_value = question_details.get(option_key, "")
		is_correct_value = question_details.get(is_correct_key, 0)
		
		if option_value and option_value in answers:
			is_correct.append(is_correct_value)
		elif is_correct_value:
			is_correct.append(2)
		else:
			is_correct.append(0)

	return is_correct


def check_input_answers(question, answer):
	# Resolve the actual LMS Question ID
	actual_question_id = resolve_question_id(question)
	
	fields = []
	for num in range(1, 5):
		fields.append(f"possibility_{cstr(num)}")

	question_details = frappe.db.get_value("LMS Question", actual_question_id, fields, as_dict=1)
	
	# Kiểm tra nếu question_details là None
	if not question_details:
		frappe.throw(_("Question not found: {0}").format(actual_question_id))
	
	for num in range(1, 5):
		possibility_key = f"possibility_{num}"
		current_possibility = question_details.get(possibility_key, "")
		
		if current_possibility and fuzz.token_sort_ratio(clean_text(current_possibility), clean_text(answer)) > 85:
			return 1

	return 0


@frappe.whitelist(allow_guest=True)
def validate_candidate_email(quiz_id, candidate_email):
	"""
		Xác thực email của ứng viên được cung cấp trùng khớp với ứng viên hiện có trong hệ thống.
	"""
	try:
		# Kiểm tra xem quiz có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			return {"success": False, "message": "Bài kiểm tra không tồn tại"}
			
		if not candidate_email:
			return {"success": False, "message": "Thiếu thông tin email ứng viên"}
		
		# Kiểm tra định dạng email
		if not validate_email_format(candidate_email):
			return {"success": False, "message": "Định dạng email không hợp lệ"}
			
		# Kiểm tra xem email có tồn tại trong ATS_Candidate không
		candidate_exists = frappe.db.exists("ATS_Candidate", {"can_email": candidate_email})
		if not candidate_exists:
			return {"success": False, "message": "Email không thuộc về ứng viên nào trong hệ thống"}
			
		# Trả về thành công nếu tất cả kiểm tra đều qua
		return {"success": True, "message": "Ứng viên được phép làm bài kiểm tra"}
		
	except Exception as e:
		frappe.logger().error(f"Quiz access validation error: {str(e)}")
		return {"success": False, "message": str(e)}

def validate_email_format(email):
	"""validation email format"""
	import re
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	return bool(re.match(pattern, email))


@frappe.whitelist()
def generate_quiz_token(quiz_id, position_id, candidate_email=None, send_email_to_candidates=False):
	"""
	Tạo token bảo mật cho bài kiểm tra dựa trên position và email ứng viên
	Nếu send_email_to_candidates=True, đồng thời gửi email cho ứng viên
	"""
	try:
		# Kiểm tra quyền truy cập
		if not frappe.has_permission("LMS Quiz", "read"):
			frappe.throw(_("Not permitted"), frappe.PermissionError)
			
		# Kiểm tra quiz có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			frappe.throw(_("Invalid quiz ID"), frappe.DoesNotExistError)
			
		# Kiểm tra position có tồn tại không (nếu có)
		if position_id and not frappe.db.exists("ATS_Position", position_id):
			frappe.throw(_("Invalid position ID"), frappe.DoesNotExistError)
			
		# Lấy secret key từ cấu hình site, nếu không có thì tạo một key cố định
		secret = frappe.get_site_config().get("auto_login_secret", "default_secret_key_for_quiz_access")
		
		# Tạo token đơn giản với kết hợp dữ liệu bao gồm email
		import hashlib
		
		# Kết hợp quiz_id, position_id và candidate_email với secret
		data = f"{quiz_id}:{position_id or ''}:{candidate_email or ''}:{secret}"
		
		# Tạo token với SHA256
		token = hashlib.sha256(data.encode('utf-8')).hexdigest()
		
		# Ghi log thành công
		frappe.logger().info(f"Token generated for quiz {quiz_id}, position {position_id}, candidate {candidate_email}")
		
		# Nếu cần gửi email cho ứng viên
		if send_email_to_candidates:
			send_quiz_email_to_candidates(quiz_id, position_id, candidate_email, token)
		
		# Trả về token
		return {
			"token": token,
			"quiz_id": quiz_id,
			"position_id": position_id,
			"candidate_email": candidate_email
		}
		
	except Exception as e:
		frappe.log_error(f"Error generating quiz token: {str(e)}")
		frappe.throw(_("Could not generate secure token"))


@frappe.whitelist()
def send_quiz_email_to_candidates(quiz_id, position_id, candidate_email, token=None):
	"""
	Gửi email thông báo bài kiểm tra cho ứng viên dựa trên position
	
	Args:
		quiz_id: ID của bài kiểm tra
		position_id: ID của position
		candidate_email: Email của ứng viên
		token: Token bảo mật (nếu đã có). Nếu không có, hàm sẽ tạo token mới.
	"""
	try:
		# Kiểm tra quyền truy cập
		if not frappe.has_permission("LMS Quiz", "read"):
			print("Not permitted")
			frappe.throw(_("Not permitted"), frappe.PermissionError)
		
		# Kiểm tra quiz có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			print("Invalid quiz ID")
			frappe.throw(_("Invalid quiz ID"), frappe.DoesNotExistError)
			
		# Kiểm tra position có tồn tại không (nếu có)
		if position_id and not frappe.db.exists("ATS_Position", position_id):
			print("Invalid position ID")
			frappe.throw(_("Invalid position ID"), frappe.DoesNotExistError)
   
		print("Valid quiz and position")
		
		# Nếu không có token, tạo token mới
		if not token:
			# Lấy secret key từ cấu hình site
			secret = frappe.get_site_config().get("auto_login_secret", "default_secret_key_for_quiz_access")
			
			# Tạo token bao gồm email ứng viên
			import hashlib
			data = f"{quiz_id}:{position_id or ''}:{candidate_email}:{secret}"
			token = hashlib.sha256(data.encode('utf-8')).hexdigest()
		
		# Lấy thông tin của quiz
		quiz = frappe.get_doc("LMS Quiz", quiz_id)
		
		# Tạo link bài kiểm tra với token
		quiz_link = f"{request.host_url.rstrip('/')}/mbw_ats/public-quiz/{quiz_id}?token={token}"
		print("Quiz link: ", quiz_link)

		# print(f"Quiz link: {quiz_link}")
		
		# Lấy danh sách ứng viên thuộc position qua job opening
		# candidates = frappe.get_all(
		#     "ATS_Candidate",
		#     filters={
		#         "job_opening_id": ["in", frappe.get_all("ATS_JobOpening", filters={"jo_position": position_id}, pluck="name")]
		#     },
		#     fields=["name", "can_email", "can_full_name"]
		# )
		print("Candidate email: ", candidate_email)
		# Tìm ứng viên theo email từ các job opening có cùng position
		job_openings_with_position = []
		if position_id:
			job_openings_with_position = frappe.get_all(
				"ATS_JobOpening", 
				filters={"jo_position": position_id}, 
				pluck="name"
			)
		
		candidate_doc = frappe.get_all(
			"ATS_Candidate",
			filters={
				"can_email": candidate_email,
				"job_opening_id": ["in", job_openings_with_position] if job_openings_with_position else ""
			},
			fields=["name", "can_email", "can_full_name", "job_opening_id"]
		)
		print("Candidate doc: ", candidate_doc)
		
		if not candidate_doc:
			return {
				"success": False,
				"message": _("No candidate found with this email for the position"),
				"sent_count": 0
			}
		
		candidate = candidate_doc[0]
		
		# Lấy thông tin position
		position_name = ""
		if position_id:
			position_name = frappe.db.get_value("ATS_Position", position_id, "position_name") or position_id
		
		# Đếm số email đã gửi thành công
		sent_count = 0
		
		if not candidate.get("can_email"):
			frappe.logger().warning(f"Ứng viên {candidate.get('name')} không có email")
			
		try:
			# Tạo nội dung email cá nhân hóa
			email_template = """
			<div style="font-family: Arial, Helvetica, sans-serif; color: #333333;">
				<p>Kính gửi <strong>{candidate_name}</strong>,</p>
				
				<p>Cảm ơn bạn đã quan tâm đến vị trí <strong>{position_name}</strong> tại công ty chúng tôi. Chúng tôi rất vui mừng thông báo rằng hồ sơ của bạn đã được xem xét và bạn đã được mời tham gia bài kiểm tra đánh giá.</p>
				
				<div style="margin: 20px 0; padding: 15px; border-left: 4px solid #0066cc; background-color: #f5f5f5;">
					<h3 style="margin-top: 0; color: #0066cc;">Thông tin bài kiểm tra:</h3>
					<ul style="padding-left: 20px;">
						<li>Tên bài kiểm tra: <strong>{quiz_title}</strong></li>
						<li>Vị trí ứng tuyển: <strong>{position_name}</strong></li>
					</ul>
				</div>
				
				<p>Vui lòng nhấn vào nút bên dưới để bắt đầu bài kiểm tra của bạn:</p>
				
				<div style="text-align: center; margin: 25px 0;">
					<a href="{quiz_link}" style="display: inline-block; padding: 12px 24px; background-color: #0066cc; color: #ffffff; text-decoration: none; font-weight: bold; border-radius: 4px;">BẮT ĐẦU KIỂM TRA</a>
				</div>
				
				<p>Một số lưu ý quan trọng:</p>
				<ul style="padding-left: 20px;">
					<li>Đảm bảo bạn có kết nối internet ổn định</li>
					<li>Hoàn thành bài kiểm tra trong một lần (không thoát ra giữa chừng)</li>
					<li>Bài kiểm tra này đánh giá kỹ năng và kiến thức liên quan đến vị trí của bạn</li>
				</ul>
				
				<p>Nếu bạn gặp bất kỳ khó khăn kỹ thuật nào, vui lòng trả lời email này để được hỗ trợ.</p>
				
				<p>Chúc bạn may mắn!</p>
				
				<div style="margin-top: 30px; border-top: 1px solid #dddddd; padding-top: 20px; color: #666666; font-size: 0.9em;">
					<p>Trân trọng,<br>
					Phòng Nhân sự<br>
					Công ty</p>
					
					<p style="font-size: 0.8em; color: #999999;">Email này được gửi tự động. Vui lòng không trả lời trực tiếp.</p>
				</div>
			</div>
			"""
			
			# Tiêu đề email
			email_subject = f"Thông báo: Bài kiểm tra cho vị trí {position_name or position_id}"
			
			# Gửi email cho từng ứng viên
			
			# candidates = frappe.get_all(
			# 	"ATS_Candidate",
			# 	filters={"job_opening_id": job_opening_id},
			# 	fields=["name", "can_email", "can_full_name"]
			# )
   
			print(f"Quiz link: {quiz_link}")

			if not candidate.get("can_email"):
				frappe.logger().warning(f"Ứng viên {candidate.get('name')} không có email")
				
			try:
				# Tạo nội dung email cá nhân hóa
				email_content = email_template.format(
					candidate_name=candidate.get("can_full_name") or "Ứng viên",
					position_name=position_name or "Vị trí ứng tuyển",
					quiz_title=quiz.title,
					quiz_link=quiz_link
				)
					
				# Gửi email trực tiếp bằng frappe.sendmail
				# frappe.sendmail(
				# 	recipients=[candidate.get("can_email")],  # Đảm bảo recipients là list với 1 email
				# 	subject=email_subject,
				# 	message=email_content,
				# 	reference_doctype="ATS_Candidate",
				# 	reference_name=candidate.get("name"),
				# 	expose_recipients=None,  # Ẩn người nhận khác
				# 	send_priority=1,  # Ưu tiên gửi cao nhất
				# )
				
				send_email(
					doctype="ATS_Candidate",
					docname=candidate.get("name"),
					recipients=[candidate.get("can_email")],
					subject=email_subject,
					content=email_content,
				)
					
				# Ghi log thành công
				frappe.logger().info(f"Đã gửi link bài kiểm tra {quiz_id} cho ứng viên {candidate.get('name')} ({candidate.get('can_email')})")
				print(f"Đã gửi link bài kiểm tra {quiz_id} cho ứng viên {candidate.get('name')} ({candidate.get('can_email')})")
				sent_count += 1
				
			except Exception as e:
				frappe.logger().error(f"Lỗi khi gửi email cho ứng viên {candidate.get('name')}: {str(e)}")
				print(f"Lỗi khi gửi email cho ứng viên {candidate.get('name')}: {str(e)}")
			
			# Trả về kết quả
			return {
				"success": True,
				"message": _("Test email sent to {0} candidates").format(sent_count),
				"sent_count": sent_count,
				# "total_candidates": len(candidates)
			}
			
		except Exception as e:
			frappe.log_error(f"Error sending quiz emails: {str(e)}")
			return {
				"success": False,
				"message": str(e),
				"sent_count": 0
			}
		
	except Exception as e:
		frappe.log_error(f"Error sending quiz emails: {str(e)}")
		return {
			"success": False,
			"message": str(e),
			"sent_count": 0
		}


@frappe.whitelist()
def get_candidate_quiz_submissions(candidate_email):
	"""
	Lấy tất cả kết quả bài thi của một ứng viên dựa trên email
	"""
	if not candidate_email:
		return []
		
	try:
		# Thêm print để debug với output dễ thấy
		print("\n\n===== DEBUG: CANDIDATE EMAIL =====")
		print(f"Tìm kết quả bài thi cho email: '{candidate_email}'")
		
		# Kiểm tra email tồn tại trong database hay không bằng SQL trực tiếp
		direct_sql_query = f"""
			SELECT name, member_candidate 
			FROM `tabLMS Quiz Submission` 
			WHERE member_candidate = '{candidate_email}'
			LIMIT 5
		"""
		
		direct_result = frappe.db.sql(direct_sql_query, as_dict=1)
		print("\n===== KẾT QUẢ TRUY VẤN TRỰC TIẾP =====")
		print(f"Số kết quả tìm được: {len(direct_result)}")
		for row in direct_result:
			print(f"ID: {row.get('name')}, Email lưu: {row.get('member_candidate') or row.get('member_email')}")
		
		# Kiểm tra cấu trúc bảng SQL
		table_structure = frappe.db.sql("""DESCRIBE `tabLMS Quiz Submission`""", as_dict=1)
		print("\n===== CẤU TRÚC BẢNG =====")
		fields_list = [f"{row.get('Field')} ({row.get('Type')})" for row in table_structure]
		print(f"Các trường trong bảng: {', '.join(fields_list)}")
		
		# Lấy tổng số bài nộp trong hệ thống
		total_submissions = frappe.db.count("LMS Quiz Submission")
		print(f"\nTổng số bài nộp trong hệ thống: {total_submissions}")
		
		# Kiểm tra một số bài nộp gần đây nhất
		latest_submissions = frappe.db.sql("""
			SELECT name, member_candidate, creation 
			FROM `tabLMS Quiz Submission` 
			ORDER BY creation DESC
			LIMIT 5
		""", as_dict=1)
		
		print("\n===== 5 BÀI NỘP GẦN NHẤT =====")
		for sub in latest_submissions:
			print(f"ID: {sub.get('name')}, Email: {sub.get('member_candidate') or 'N/A'}, Created: {sub.get('creation')}")
		
		# Thử một số phương pháp tìm kiếm khác nhau
		print("\n===== THỬ CÁC PHƯƠNG PHÁP TÌM KIẾM KHÁC =====")
		
		# Phương pháp 1: frappe.get_all với trường member_candidate (cách thường dùng)
		submissions = frappe.get_all(
			"LMS Quiz Submission",
			filters={"member_candidate": candidate_email},
			fields=["name", "quiz", "score", "score_out_of", "percentage", "creation", "quiz_title"],
			order_by="creation desc"
		)
		print(f"Phương pháp 1 (member_candidate={candidate_email}): {len(submissions)} kết quả")
		
		# Phương pháp 2: frappe.get_all với SQL LIKE
		submissions_like = frappe.get_all(
			"LMS Quiz Submission",
			filters=[["member_candidate", "like", f"%{candidate_email}%"]],
			fields=["name", "quiz", "score", "score_out_of", "percentage", "creation", "quiz_title"],
			order_by="creation desc"
		)
		print(f"Phương pháp 2 (LIKE): {len(submissions_like)} kết quả")
		
		# Phương pháp 3: SQL trực tiếp (không phân biệt chữ hoa/thường)
		case_insensitive = frappe.db.sql(f"""
			SELECT name, quiz, score, score_out_of, percentage, creation, quiz_title 
			FROM `tabLMS Quiz Submission`
			WHERE LOWER(member_candidate) = LOWER('{candidate_email}') 
			   
			ORDER BY creation DESC
		""", as_dict=1)
		print(f"Phương pháp 3 (case-insensitive): {len(case_insensitive)} kết quả")
		
		# Nếu tìm theo member_candidate không có kết quả, thử tìm theo member_email
		if not submissions:
			submissions = frappe.get_all(
				"LMS Quiz Submission",
				filters={"member_candidate": candidate_email},
				fields=["name", "quiz", "score", "score_out_of", "percentage", "creation", "quiz_title"],
				order_by="creation desc"
			)
			print(f"Phương pháp 4 (member_candidate={candidate_email}): {len(submissions)} kết quả")
		
		# Nếu vẫn không có kết quả, thử truy vấn theo member (user)
		if not submissions:
			user = frappe.db.get_value("User", {"email": candidate_email}, "name")
			if user:
				submissions = frappe.get_all(
					"LMS Quiz Submission",
					filters={"member": user},
					fields=["name", "quiz", "score", "score_out_of", "percentage", "creation", "quiz_title"],
					order_by="creation desc"
				)
				print(f"Phương pháp 5 (member={user}): {len(submissions)} kết quả")
		
		# Nếu có kết quả từ phương pháp khác, ưu tiên sử dụng
		if not submissions and case_insensitive:
			submissions = case_insensitive
			print("Sử dụng kết quả từ phương pháp case-insensitive")
		elif not submissions and submissions_like:
			submissions = submissions_like
			print("Sử dụng kết quả từ phương pháp LIKE")
			
		# Kết luận
		print(f"\n===== KẾT LUẬN =====")
		print(f"Tìm thấy {len(submissions)} kết quả bài thi cho ứng viên {candidate_email}")
		if submissions:
			print(f"Bài nộp đầu tiên: {submissions[0]}")
		print("===== KẾT THÚC DEBUG =====\n\n")
		
		# Thêm thông tin chi tiết về bài thi
		for submission in submissions:
			# Lấy tên quiz nếu chưa có
			if not submission.get("quiz_title"):
				quiz_title = frappe.db.get_value("LMS Quiz", submission["quiz"], "title")
				submission["quiz_title"] = quiz_title or submission["quiz"]
			
			# Làm tròn phần trăm
			submission["percentage"] = round(float(submission["percentage"] or 0))
		
		return submissions
		
	except Exception as e:
		print(f"\n\nERROR in get_candidate_quiz_submissions: {str(e)}\n\n")
		frappe.log_error(f"Error fetching quiz submissions for {candidate_email}: {str(e)}")
		return []


def update_candidate_quiz_results(candidate_email, job_opening_id, submission_id):
	"""
	Cập nhật thông tin kết quả bài kiểm tra cho ứng viên
	
	Args:
		candidate_email: Email của ứng viên
		job_opening_id: ID của job opening
		submission_id: ID của bài nộp quiz
	"""
	try:
		# Kiểm tra xem ứng viên có tồn tại không
		candidates = frappe.get_all(
			"ATS_Candidate", 
			filters={"can_email": candidate_email, "job_opening_id": job_opening_id},
			fields=["name"]
		)
		
		if not candidates:
			frappe.logger().error(f"Không tìm thấy ứng viên với email {candidate_email} thuộc job opening {job_opening_id}")
			return False
			
		# Lấy chi tiết bài nộp
		submission = frappe.get_doc("LMS Quiz Submission", submission_id)
		if not submission:
			frappe.logger().error(f"Không tìm thấy bài nộp {submission_id}")
			return False
		
		# Lấy thông tin ứng viên
		candidate = frappe.get_doc("ATS_Candidate", candidates[0].name)
		
		# Thêm trường mới lưu kết quả bài thi nếu chưa có
		if not hasattr(candidate, 'quiz_results') or not candidate.quiz_results:
			candidate.quiz_results = []
		
		# Tạo bản ghi mới cho kết quả bài thi
		candidate.append('quiz_results', {
			'quiz': submission.quiz,
			'quiz_title': submission.quiz_title or frappe.db.get_value("LMS Quiz", submission.quiz, "title"),
			'score': submission.score,
			'score_out_of': submission.score_out_of,
			'percentage': submission.percentage,
			'submission_id': submission.name,
			'date_submitted': submission.creation
		})
		
		# Lưu lại ứng viên với kết quả bài thi mới
		candidate.save(ignore_permissions=True)
		frappe.db.commit()
		
		frappe.logger().info(f"Đã cập nhật kết quả bài thi {submission.quiz} cho ứng viên {candidate.name}")
		return True
		
	except Exception as e:
		frappe.logger().error(f"Lỗi khi cập nhật kết quả bài thi cho ứng viên {candidate_email}: {str(e)}")
		return False


@frappe.whitelist(allow_guest=True)
def get_public_quiz_details(quiz_id):
	"""
	Lấy thông tin cơ bản về bài kiểm tra để hiển thị trong trang làm bài công khai
	"""
	try:
		if not quiz_id:
			return {"error": "Thiếu thông tin bài kiểm tra"}
			
		# Kiểm tra bài kiểm tra có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			return {"error": "Không tìm thấy bài kiểm tra"}
			
		# Lấy thông tin cơ bản của quiz
		quiz = frappe.get_doc("LMS Quiz", quiz_id)
		
		# Trả về thông tin cần thiết
		return {
			"title": quiz.title,
			"description": quiz.description or "Vui lòng hoàn thành bài kiểm tra này",
			"total_marks": quiz.total_marks,
			"passing_percentage": quiz.passing_percentage,
			"job_opening_id": quiz.job_opening_id,
			"time_limit": quiz.time_limit if hasattr(quiz, 'time_limit') else None
		}
		
	except Exception as e:
		frappe.logger().error(f"Error getting public quiz details: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def verify_candidate(quiz_id, email, full_name=None):
	"""
	Xác minh thông tin ứng viên trước khi cho phép làm bài kiểm tra.
	Với phiên bản không đăng nhập này, chúng ta không yêu cầu xác thực nghiêm ngặt.
	"""
	try:
		if not quiz_id or not email:
			return {"success": False, "error": "Thiếu thông tin bài kiểm tra hoặc email"}
			
		# Kiểm tra bài kiểm tra có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			return {"success": False, "error": "Không tìm thấy bài kiểm tra"}
			
		# Kiểm tra định dạng email
		if not validate_email_format(email):
			return {"success": False, "error": "Định dạng email không hợp lệ"}
		
		# Lấy thông tin job opening từ quiz
		job_opening_id = frappe.db.get_value("LMS Quiz", quiz_id, "job_opening_id")
		
		# Lưu thông tin ứng viên nếu có tên
		if full_name:
			try:
				create_or_update_candidate(email, full_name, job_opening_id)
			except Exception as e:
				frappe.logger().error(f"Error saving candidate info: {str(e)}")
				# Không trả về lỗi ở đây vì chúng ta vẫn muốn cho phép ứng viên làm bài
		
		return {"success": True}
		
	except Exception as e:
		frappe.logger().error(f"Error verifying candidate: {str(e)}")
		return {"success": False, "error": str(e)}


def create_or_update_candidate(email, full_name, job_opening_id=None):
	"""
	Tạo mới hoặc cập nhật thông tin ứng viên trong hệ thống
	"""
	# Kiểm tra xem ứng viên đã tồn tại chưa
	candidate = frappe.db.exists("ATS_Candidate", {"can_email": email})
	
	if candidate:
		# Cập nhật thông tin ứng viên
		candidate_doc = frappe.get_doc("ATS_Candidate", candidate)
		candidate_doc.can_full_name = full_name
		
		# Nếu job_opening_id được cung cấp and khác với job_opening hiện tại
		if job_opening_id and candidate_doc.job_opening_id != job_opening_id:
			# Có thể cập nhật hoặc để nguyên tùy theo yêu cầu
			pass
			
		candidate_doc.save(ignore_permissions=True)
		return candidate_doc
	else:
		# Tạo mới ứng viên
		new_candidate = frappe.get_doc({
			"doctype": "ATS_Candidate",
			"can_full_name": full_name,
			"can_email": email,
			"job_opening_id": job_opening_id if job_opening_id else None,
			"source": "Quiz"  # Hoặc một nguồn phù hợp
		})
		new_candidate.insert(ignore_permissions=True)
		return new_candidate


@frappe.whitelist(allow_guest=True)
def get_public_quiz(quiz_id):
	"""
	Lấy thông tin chi tiết bài kiểm tra để hiển thị cho ứng viên làm bài
	"""
	try:
		if not quiz_id:
			return {"error": "Thiếu thông tin bài kiểm tra"}
			
		# Kiểm tra bài kiểm tra có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			return {"error": "Không tìm thấy bài kiểm tra"}
			
		# Lấy thông tin chi tiết của quiz
		quiz = frappe.get_doc("LMS Quiz", quiz_id)
		
		# Tạo danh sách câu hỏi với thông tin cần thiết
		questions = []
		for q in quiz.questions:
			question_info = {
				"name": q.name,
				"question_name": q.question,
				"question": q.question_detail,
				"type": q.type,
			}
			
			# Lấy thông tin tùy theo loại câu hỏi
			if q.type == "Choices":
				choices = []
				for i in range(1, 5):  # Giả định có tối đa 4 lựa chọn
					option_field = f"option_{i}"
					is_correct_field = f"is_correct_{i}"
					
					if hasattr(q, option_field) and getattr(q, option_field):
						# Thêm đầy đủ các trường cần thiết cho mỗi lựa chọn
						choice_data = {
							"option": getattr(q, option_field),  # Nội dung hiển thị
							"value": str(i),  # Giá trị duy nhất để xác định lựa chọn (chuyển thành string)
							"is_correct": getattr(q, is_correct_field, 0) if hasattr(q, is_correct_field) else 0  # Thêm trạng thái đúng/sai
						}
						choices.append(choice_data)
						
				question_info["choices"] = choices
				question_info["multiple"] = q.multiple if hasattr(q, 'multiple') else False
				
			questions.append(question_info)
		
		# Tùy chọn xáo trộn câu hỏi nếu có giới hạn số lượng câu hỏi
		if quiz.limit_questions_to:
			import random
			random.shuffle(questions)
			questions = questions[:int(quiz.limit_questions_to)]
		
		# Trả về thông tin quiz đầy đủ
		return {
			"id": quiz.name,
			"title": quiz.title,
			"description": quiz.description or "",
			"questions": questions,
			"total_marks": quiz.total_marks,
			"passing_percentage": quiz.passing_percentage,
			"time_limit": quiz.time_limit if hasattr(quiz, 'time_limit') else None
		}
		
	except Exception as e:
		frappe.logger().error(f"Error getting public quiz: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def submit_public_quiz(quiz_id, results, candidate_email, candidate_name=None):
	"""
	Nhận kết quả bài kiểm tra từ trang làm bài công khai
	"""
	try:
		if not quiz_id or not results or not candidate_email:
			return {"success": False, "error": "Thiếu thông tin bài nộp"}
		
		# Kiểm tra định dạng email
		if not validate_email_format(candidate_email):
			return {"success": False, "error": "Định dạng email không hợp lệ"}
			
		# Parse kết quả
		if isinstance(results, str):
			results = json.loads(html.unescape(results))
		
		# Gọi hàm xử lý quiz_summary với email ứng viên
		quiz_result = quiz_summary(quiz_id, json.dumps(results), candidate_email)
		
		# Đảm bảo lưu thông tin ứng viên nếu có tên
		if candidate_name:
			job_opening_id = frappe.db.get_value("LMS Quiz", quiz_id, "job_opening_id")
			try:
				create_or_update_candidate(candidate_email, candidate_name, job_opening_id)
			except Exception as e:
				frappe.logger().error(f"Error updating candidate after submission: {str(e)}")
		
		return {
			"success": True,
			"result": quiz_result
		}
		
	except Exception as e:
		frappe.logger().error(f"Error submitting public quiz: {str(e)}")
		return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
def validate_quiz_token(quiz_id, position_id, token, candidate_email=None):
	"""
	Kiểm tra tính hợp lệ của token truy cập bài kiểm tra
	
	Args:
		quiz_id: ID của bài kiểm tra
		position_id: ID của position (có thể là None nếu bài thi không gắn với position)
		token: Token xác thực cần kiểm tra
		candidate_email: Email ứng viên (tùy chọn, sẽ được trích xuất từ token)
		
	Returns:
		Dict: Thông tin về kết quả xác thực
	"""
	try:
		# Kiểm tra bài kiểm tra có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			frappe.throw(_("Quiz not found"))
		
		# Lấy thông tin bài kiểm tra
		quiz = frappe.get_doc("LMS Quiz", quiz_id)
		
		# Kiểm tra token
		if not token:
			return {
				"valid": False, 
				"message": _("Invalid token"),
				"reason": "invalid_token"
			}
		
		# Lấy secret key từ cấu hình site, nếu không có thì dùng key cố định
		secret = frappe.get_site_config().get("auto_login_secret", "default_secret_key_for_quiz_access")
		
		# Nếu có candidate_email, tạo token với email để so sánh
		if candidate_email:
			import hashlib
			data = f"{quiz_id}:{position_id or ''}:{candidate_email}:{secret}"
			expected_token = hashlib.sha256(data.encode('utf-8')).hexdigest()
			
			if token == expected_token:
				return {
					"valid": True,
					"quiz_id": quiz_id,
					"position_id": position_id,
					"candidate_email": candidate_email,
					"message": _("Token is valid")
				}
		
		# Nếu không có email hoặc token không khớp, thử tìm email từ token
		# Thử tất cả ứng viên trong các job opening có cùng position để tìm email phù hợp
		if position_id:
			job_openings = frappe.get_all(
				"ATS_JobOpening",
				filters={"jo_position": position_id},
				pluck="name"
			)
			
			if job_openings:
				candidates = frappe.get_all(
					"ATS_Candidate",
					filters={"job_opening_id": ["in", job_openings]},
					fields=["can_email"]
				)
				
				for candidate in candidates:
					if candidate.can_email:
						import hashlib
						data = f"{quiz_id}:{position_id}:{candidate.can_email}:{secret}"
						expected_token = hashlib.sha256(data.encode('utf-8')).hexdigest()
						
						if token == expected_token:
							return {
								"valid": True,
								"quiz_id": quiz_id,
								"position_id": position_id,
								"candidate_email": candidate.can_email,
								"message": _("Token is valid")
							}
		
		# Token không hợp lệ
		frappe.logger().info(f"Token không hợp lệ cho quiz {quiz_id}")
		return {
			"valid": False, 
			"message": _("Invalid authentication token"),
			"reason": "invalid_token"
		}
		
	except Exception as e:
		frappe.log_error(f"Error validating quiz token: {str(e)}")
		return {
			"valid": False,
			"message": str(e),
			"reason": "validation_error"
		}

@frappe.whitelist(allow_guest=True)
def auto_login_candidate(quiz_id, token):
	"""
	Xác thực token and tự động đăng nhập ứng viên để làm bài kiểm tra
	
	Args:
		quiz_id: ID của bài kiểm tra
		token: Token xác thực
		
	Returns:
		Dict: Kết quả xác thực and URL chuyển hướng nếu thành công
	"""
	try:
		# Kiểm tra bài kiểm tra có tồn tại không
		if not frappe.db.exists("LMS Quiz", quiz_id):
			return {
				"success": False,
				"message": _("Quiz not found"),
				"reason": "quiz_not_found"
			}
		
		# Lấy thông tin bài kiểm tra
		quiz = frappe.get_doc("LMS Quiz", quiz_id)
		
		# Trích xuất email từ URL query parameters nếu có
		email = frappe.form_dict.get("email")
		
		# Thử xác thực token với các position khác nhau
		all_positions = frappe.get_all("ATS_Position", pluck="name")
		validation_success = False
		
		for position_id in all_positions:
			# Xác thực token
			validation = validate_quiz_token(quiz_id, position_id, token)
			if validation["valid"]:
				validation_success = True
				break
		
		if not validation_success:
			return {
				"success": False,
				"message": _("Invalid token"),
				"reason": "invalid_token"
			}
		
		# Kiểm tra email có thuộc ứng viên trong position không
		if email and position_id:
			job_openings = frappe.get_all(
				"ATS_JobOpening",
				filters={"jo_position": position_id},
				pluck="name"
			)
			
			if job_openings:
				candidate_exists = frappe.db.exists("ATS_Candidate", {
					"can_email": email,
					"job_opening_id": ["in", job_openings]
				})
				
				if not candidate_exists:
					frappe.logger().warning(f"Candidate with email {email} not found in position {position_id}")
					# Không throw lỗi, vẫn cho phép truy cập vì token hợp lệ
		
		# Tạo URL chuyển hướng
		redirect_url = f"/mbw_ats/quiz/{quiz_id}"
		
		# Đăng nhập thành công
		return {
			"success": True,
			"message": _("Authentication successful"),
			"redirect_url": redirect_url,
			"candidate_email": email,  # Trả về email để frontend có thể sử dụng
			"quiz_title": quiz.title
		}
		
	except Exception as e:
		frappe.log_error(f"Auto login error: {str(e)}")
		return {
			"success": False,
			"message": str(e),
			"reason": "login_failed"
		}

@frappe.whitelist(allow_guest=True)
def get_quiz_user_status():
	"""
	Safe alternative to get_logged_user() for quiz takers.
	Returns user information or guest status for quiz access.
	This allows quiz to be accessible by guests without authentication.
	"""
	try:
		user = frappe.session.user
		is_guest = (user == "Guest")
		
		return {
			"success": True,
			"user": user,
			"is_guest": is_guest,
			"email": None if is_guest else frappe.db.get_value("User", user, "email")
		}
	except Exception as e:
		frappe.logger().error(f"Error in get_quiz_user_status: {str(e)}")
		return {
			"success": True,
			"user": "Guest",
			"is_guest": True,
			"email": None
		}

@frappe.whitelist(allow_guest=True)
def allow_guest_access_to_quiz():
	"""
	Always allow guest access to quiz functionality.
	This is a replacement for checking System Settings.
	
	Returns:
		bool: Always returns True to allow guest access to quiz
	"""
	return True

def check_quiz_access_permission(quiz_id=None, token=None, email=None):
	"""
	Centralized function to check access permissions for quiz.
	For guest users, always grants access instead of checking System Settings.
	
	Args:
		quiz_id: ID of the quiz
		token: Authentication token
		email: Email of the candidate
		
	Returns:
		bool: True if access is allowed, False otherwise
	"""
	if frappe.session.user == "Guest":
		# Guest is allowed if they have a valid token
		if token and quiz_id:
			job_opening_id = frappe.db.get_value("LMS Quiz", quiz_id, "job_opening_id") 
			validation = validate_quiz_token(quiz_id, job_opening_id, token)
			if validation and validation.get("valid"):
				return True
		
		# If email is provided, check if it belongs to a candidate
		if email and quiz_id:
			job_opening_id = frappe.db.get_value("LMS Quiz", quiz_id, "job_opening_id")
			if job_opening_id:
				candidate_exists = frappe.db.exists("ATS_Candidate", {
					"can_email": email,
					"job_opening_id": job_opening_id
				})
				if candidate_exists:
					return True
		
		return True  # Always allow guest access for quiz
	else:
		# Logged-in users follow normal permission checks
		return frappe.has_permission("LMS Quiz", doc=quiz_id)

@frappe.whitelist(allow_guest=True)
def check_candidate_knockout_status(quiz_id, member_email=None):
    """
    Kiểm tra xem ứng viên đã bị knockout trong quiz này chưa
    
    Args:
        quiz_id: ID của bài kiểm tra
        member_email: Email của ứng viên
        
    Returns:
        Dict: Thông tin về trạng thái knockout
    """
    try:
        if not frappe.db.exists("LMS Quiz", quiz_id):
            return {"success": False, "message": "Quiz not found"}
            
        # Chuẩn bị các filter
        filters = {"quiz": quiz_id, "is_knocked_out": 1}
        
        # Người dùng hiện tại nếu không có email cung cấp
        current_user = frappe.session.user
        
        if current_user == "Guest" or member_email:
            if member_email:
                filters["member_candidate"] = member_email
        else:
            filters["member"] = current_user
            
        # Tìm bài nộp bị knockout
        knockout_submission = frappe.get_all(
            "LMS Quiz Submission",
            filters=filters,
            fields=["name", "creation", "knockout_question", "quiz_title"],
            order_by="creation desc",
            limit=1
        )
        
        if knockout_submission:
            submission = knockout_submission[0]
            return {
                "success": True,
                "is_knocked_out": True,
                "submission_id": submission.get("name"),
                "knockout_date": submission.get("creation"),
                "knockout_question": submission.get("knockout_question"),
                "quiz_title": submission.get("quiz_title"),
                "message": "Candidate has been knocked out from this quiz"
            }
        else:
            return {
                "success": True,
                "is_knocked_out": False,
                "message": "Candidate has not been knocked out"
            }
        
    except Exception as e:
        frappe.log_error(f"Error checking knockout status: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def count_quiz_attempts(quiz_id, member_email=None):
    """
    Đếm số lần làm bài kiểm tra của ứng viên
    
    Args:
        quiz_id: ID của bài kiểm tra
        member_email: Email của ứng viên (tùy chọn)
        
    Returns:
        Dict: Thông tin số lần làm bài và giới hạn số lần làm bài
    """
    try:
        if not frappe.db.exists("LMS Quiz", quiz_id):
            return {"success": False, "message": "Quiz not found", "attempt_count": 0}
            
        # Lấy thông tin giới hạn số lần làm bài
        max_attempts = frappe.db.get_value("LMS Quiz", quiz_id, "max_attempts")
        print(f"Max attempts configured: {max_attempts}")
        
        # Chuẩn bị các filter
        filters = {"quiz": quiz_id}
        
        # Người dùng hiện tại nếu không có email cung cấp
        current_user = frappe.session.user
        
        if current_user == "Guest" or member_email:
            if member_email:
                filters["member_candidate"] = member_email
        else:
            filters["member"] = current_user
            
            # Lấy email của người dùng hiện tại
            if current_user != "Guest":
                user_email = frappe.db.get_value("User", current_user, "email")
        
        
        # Đếm số bài nộp
        attempt_count = frappe.db.count("LMS Quiz Submission", filters=filters)
        
        # Kiểm tra chi tiết 5 bài nộp gần nhất để debug
        recent_submissions = frappe.get_all(
            "LMS Quiz Submission",
            filters=filters,
            fields=["name", "member", "member_candidate", "creation"],
            order_by="creation desc",
            limit=5
        )
        
        
        # Kết luận
        is_max_reached = max_attempts and attempt_count >= max_attempts
        return {
            "success": True,
            "attempt_count": attempt_count,
            "max_attempts": max_attempts,
            "is_max_reached": is_max_reached,
            "recent_submissions": recent_submissions
        }
        
    except Exception as e:
        frappe.log_error(f"Error counting quiz attempts: {str(e)}")
        return {"success": False, "message": str(e), "attempt_count": 0}

@frappe.whitelist(allow_guest=True)
def extract_candidate_from_token(quiz_id, token):
	"""
	Trích xuất thông tin ứng viên từ token
	
	Args:
		quiz_id: ID của bài kiểm tra
		token: Token xác thực
		
	Returns:
		Dict: Thông tin ứng viên nếu token hợp lệ
	"""
	try:
		# Lấy thông tin quiz
		quiz = frappe.get_doc("LMS Quiz", quiz_id)
		
		# Thử với nhiều position_id khác nhau để tìm token hợp lệ
		# Bởi vì chúng ta không lưu position_id trong quiz nữa
		all_positions = frappe.get_all("ATS_Position", pluck="name")
		
		for position_id in all_positions:
			# Validate token và lấy email
			validation_result = validate_quiz_token(quiz_id, position_id, token)
			
			if validation_result.get("valid") and validation_result.get("candidate_email"):
				candidate_email = validation_result.get("candidate_email")
				
				# Lấy job openings có position này
				job_openings = frappe.get_all(
					"ATS_JobOpening",
					filters={"jo_position": position_id},
					pluck="name"
				)
				
				if job_openings:
					# Lấy thông tin chi tiết của ứng viên
					candidate = frappe.get_all(
						"ATS_Candidate",
						filters={
							"can_email": candidate_email, 
							"job_opening_id": ["in", job_openings]
						},
						fields=["name", "can_email", "can_full_name"],
						limit=1
					)
					
					if candidate:
						return {
							"success": True,
							"candidate_email": candidate_email,
							"candidate_name": candidate[0].get("can_full_name"),
							"candidate_id": candidate[0].get("name")
						}
		
		return {
			"success": False,
			"message": "Invalid token or candidate not found"
		}
			
	except Exception as e:
		frappe.log_error(f"Error extracting candidate from token: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}
