import frappe
from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype

def copy_perms(parent):
	"""Copy all DocPerm in to Custom DocPerm for the given document"""
	for d in frappe.get_all("DocPerm", fields="*", filters=dict(parent=parent)):
		custom_perm = frappe.new_doc("Custom DocPerm")
		custom_perm.update(d)
		custom_perm.insert(ignore_permissions=True)

def setup_custom_perms(parent):
	"""if custom permssions are not setup for the current doctype, set them up"""
	if not frappe.db.exists("Custom DocPerm", dict(parent=parent)):
		copy_perms(parent)
		return True

@frappe.whitelist()
def add_role_to_doctypes(role, doctypes=None):
	if isinstance(doctypes, str):
		doctypes = frappe.parse_json(doctypes)

	if not doctypes:
		doctypes = ["ATS_Candidate", "ATS_JobOpening"]

	for dt in doctypes:
		setup_custom_perms(dt)

		# Check xem đã tồn tại trong Custom DocPerm chưa
		exists = frappe.db.exists("Custom DocPerm", {
			"parent": dt,
			"role": role,
			"permlevel": 0,
			"if_owner": 0
		})

		if not exists:
			# Tạo mới Custom DocPerm
			doc = frappe.get_doc({
				"doctype": "Custom DocPerm",
				"parent": dt,
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"permlevel": 0,
				"read": 0,
				"export": 0,
				"cancel": 0,
				"amend": 0,
				"print": 0,
				"email": 0,
				"report": 0,
				"import": 0,
				"select": 0,
				"delete": 0,
				"share": 0,
				# các quyền khác mặc định là 0
			})
			doc.insert(ignore_permissions=True)

			# Validate lại quyền để Frappe load từ Custom DocPerm
			validate_permissions_for_doctype(dt)

		# # 🔽 Phần thêm mới để cập nhật cả listPermission trong DocType (UI)
		# dt_doc = frappe.get_doc("DocType", dt)
		# already_in_list = any(
		# 	p.role == role and p.permlevel == 0 and not p.if_owner
		# 	for p in dt_doc.permissions
		# )
		# if not already_in_list:
		# 	dt_doc.append("permissions", {
		# 		"role": role,
		# 		"permlevel": 0,
		# 		"read": 1,
		# 		"export": 0,
		#         "write": 0,
		#         "create": 0,
		#         "submit": 0,
		#         "cancel": 0,
		#         "amend": 0,
		#         "print": 0,
		#         "email": 0,
		#         "report": 0,
		#         "import": 0,
		#         "select": 0,
		#         "delete": 0,
		#         "export": 0,
		#         "share": 0,
		#         "if_owner": 0,
		# 	})
		# 	dt_doc.save()

	return {
		"status": "success",
		"message": f"Role '{role}' added to {len(doctypes)} doctypes with default permissions."
	}
 
@frappe.whitelist()
def ensure_read_perms_for_role(role: str):
	fixed_doctypes = [
		"ATS_CandidateSource",
		"ATS_Major",
		"ATS_Institution",
		"ATS_Company",
		"ATS_Unit",
		"ATS_Profession",
		"ATS_Level",
		"ATS_Location",
		"ATS_Position",
		"ATS_Institution",
		"ATS_Major",
		"ATS_CandidateLabel",
		"ATS_CandidateSourceGroup",
		"ATS_CandidateSource",
		"ATS_RejectReason",
		"ATS_RejectReasonGroup",
		"ATS_RejectReasonCampaign",
		"ATS_RejectReasonCampaignGroup",
		"ATS_Recruitment_Process",
		"ATS_EvaluationTemplate",
		"ATS_EvaluationCriteria",
		"ATS_EvaluationTemplateCriteria",
		"ATS_Evaluation",
		"ATS_Email_Template",
	]

	added = []

	for dt in fixed_doctypes:
		# Đảm bảo có bản ghi Custom DocPerm
		if not frappe.db.exists("Custom DocPerm", {"parent": dt}):
			from frappe.core.doctype.doctype.doctype import make_module_and_roles
			from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
			# Tạo bản sao nếu chưa có
			for p in frappe.get_all("DocPerm", fields="*", filters={"parent": dt}):
				perm = frappe.new_doc("Custom DocPerm")
				perm.update(p)
				perm.insert(ignore_permissions=True)

		# Kiểm tra xem role đã có chưa
		exists = frappe.db.exists("Custom DocPerm", {
			"parent": dt,
			"role": role,
			"permlevel": 0,
			"if_owner": 0,
		})

		if not exists:
			# Thêm quyền read mặc định
			frappe.get_doc({
				"doctype": "Custom DocPerm",
				"parent": dt,
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"permlevel": 0,
				"read": 1,
				"export": 0,
			}).insert(ignore_permissions=True)

			added.append(dt)

			# Validate lại
			from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
			validate_permissions_for_doctype(dt)

	return {"added": added}

@frappe.whitelist()
def delete_role_and_perms(role: str):
	perms = frappe.get_all("Custom DocPerm", filters={"role": role}, pluck="name")
	for name in perms:
		frappe.delete_doc("Custom DocPerm", name, force=True)

	role_doc = frappe.get_doc("Role", role)
	if not role_doc.is_custom:
		frappe.throw("Không thể xoá role hệ thống")

	frappe.delete_doc("Role", role, force=True)

# ✅ API 1: Lấy danh sách user có role hệ thống tuyển dụng (role ATS)
@frappe.whitelist()
def get_users():
	ats_roles = get_ats_roles_internal()
	users = set()

	for role in ats_roles:
		result = get_users_by_role(role)
		users.update([u["name"] for u in result])

	users.discard("Administrator")
	users.discard("Guest")

	search = frappe.form_dict.get("search", "")
	if not isinstance(search, str):
		search = str(search)
	search = search.lower().strip()

	user_list = frappe.get_all(
		"User",
		filters={
			"name": ["in", list(users)],
			"enabled": 1,
		},
		fields=["name", "full_name", "email", "username"]
	)

	final_users = []
	for user in user_list:
		# Tìm kiếm nếu có từ khóa
		if search:
			if not (
				search in (user.get("name") or "").lower()
				or search in (user.get("email") or "").lower()
				or search in (user.get("full_name") or "").lower()
				or search in (user.get("username") or "").lower()
			):
				continue

		user_doc = frappe.get_doc("User", user.name)
		user_doc.load_from_db()

		# Chỉ lấy user không bị block MBW ATS
		blocked_modules = [m.module for m in (user_doc.block_modules or [])]
		if "MBW ATS" not in blocked_modules:
			final_users.append(user)

	return final_users

# ✅ API 2: Lấy danh sách role hệ thống ATS (theo module 'MBW ATS')
@frappe.whitelist()
def get_ats_roles():
	return get_ats_roles_internal()

# ✅ API 3: Lấy danh sách role của một user cụ thể
@frappe.whitelist(allow_guest=True)
def get_user_roles(user):
	try:
		# Xử lý trường hợp đặc biệt cho người dùng Guest
		if user == "Guest":
			return ["Guest"]
			
		doc = frappe.get_doc("User", user)
		return [r.role for r in doc.roles]
	except Exception as e:
		frappe.logger().error(f"Error in get_user_roles for {user}: {str(e)}")
		return ["Guest"] # Trả về quyền tối thiểu trong trường hợp lỗi

# ✅ API 4: Cập nhật lại toàn bộ role cho một user
@frappe.whitelist()
def update_user_roles(user, roles):
	roles = frappe.parse_json(roles) if isinstance(roles, str) else roles

	user_doc = frappe.get_doc("User", user)
	user_doc.roles = []

	for idx, role in enumerate(roles):
		user_doc.append("roles", {
			"doctype": "Has Role",
			"parenttype": "User",
			"parent": user,
			"role": role,
			"idx": idx + 1
		})

	user_doc.save()
	frappe.db.commit()
	return {"message": "Roles updated"}

# 🧠 Internal: Lấy danh sách roles theo module MBW ATS
def get_ats_roles_internal():
	default_roles = [
		"Applicant",
		"Hiring Manager",
		"HR Staff",
		"Interviewer",
		"Recruiter"
	]

	# Lấy các role có is_custom = 1
	custom_roles = frappe.get_all(
		"Role",
		filters={"is_custom": 1},
		pluck="name"
	)

	return list(set(default_roles + custom_roles))

def get_users_by_role(role_name=None):
	#Lấy danh sách parrent distinct theo name
	user_ids = frappe.db.sql("""
		SELECT u.name AS user_name, hr.parent
		FROM `tabHas Role` hr
		JOIN `tabUser` u ON u.name = hr.parent
		WHERE hr.role = %s AND u.enabled = 1
		GROUP BY u.name
	""", role_name, as_dict=True)

	ids = [u["parent"] for u in user_ids]

	users = frappe.get_all(
		"User",
		filters={"name": ["in", ids], "enabled": 1},
		fields=["name", "full_name", "email", "username"],
		ignore_permissions=True
	)

	return users

@frappe.whitelist(allow_guest=True)
def get_all_docperms_for_roles(roles: list = None):
	if not roles:
		roles = frappe.get_roles(frappe.session.user)

	perms = frappe.get_all(
		"Custom DocPerm",
		filters={"role": ["in", roles]},
		fields=[
		  "role", 
		  "read", 
		  "select", 
		  "create", 
		  "delete", 
		  "submit",
		  "cancel",
		  "amend",
		  "print",
		  "email",
		  "report",
		  "import",
		  "export",
		  "share",
		  "write",
		  "parent as doctype"],
		limit_page_length=1000
	)

	return perms

@frappe.whitelist()
def add_user_to_ats(user, roles):
	if user == "Administrator":
		frappe.throw(("Cannot modify Administrator account."))

	roles = frappe.parse_json(roles) if isinstance(roles, str) else roles
	user_doc = frappe.get_doc("User", user)

	# Bỏ hết và thêm lại đúng MBW ATS
	user_doc.set("allow_modules", ["Go1 CMS"])

	# Add roles nếu chưa có
	existing_roles = {r.role for r in user_doc.roles}
	for r in roles:
		if r not in existing_roles:
			user_doc.append("roles", {"role": r})

	user_doc.save()
	frappe.db.commit()
	return {"status": "added"}



@frappe.whitelist()
def remove_user_from_ats(user):
	if user == "Administrator":
		frappe.throw(("Cannot remove Administrator from ATS."))

	ats_roles = get_ats_roles_internal()
	user_doc = frappe.get_doc("User", user)

	# Xoá roles thuộc ATS
	user_doc.roles = [r for r in user_doc.roles if r.role not in ats_roles]

	# Xoá khỏi allow_modules nếu có
	modules = set(user_doc.get("allow_modules") or [])
	if "MBW ATS" in modules:
		modules.remove("MBW ATS")
		user_doc.set("allow_modules", list(modules))

	user_doc.save()
	frappe.db.commit()
	return {"status": "removed"}


@frappe.whitelist()
def get_users_not_in_ats():
	# Tất cả user đang active và không phải Administrator
	all_users = frappe.get_all(
		"User",
		filters={
			"enabled": 1,
			"name": ["!=", "Administrator"]
		},
		fields=["name", "full_name", "email", "username"]
	)

	ats_roles = get_ats_roles_internal()

	# Lấy toàn bộ user đã có role ATS
	users_with_ats_roles = set()
	for role in ats_roles:
		role_users = get_users_by_role(role)
		users_with_ats_roles.update([u["name"] for u in role_users])

	# Lọc ra user chưa có role ATS
	users_not_in_ats = [u for u in all_users if u.name not in users_with_ats_roles]

	return users_not_in_ats


