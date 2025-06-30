import frappe
from frappe.translate import get_all_translations
from frappe.utils.telemetry import POSTHOG_HOST_FIELD, POSTHOG_PROJECT_FIELD

@frappe.whitelist(allow_guest=True)
def get_translations(lang=None):
    if lang:
        language = lang
    else:
        if frappe.session.user != "Guest":
            language = frappe.db.get_value(
                "User", frappe.session.user, "language")
        else:
            language = frappe.db.get_single_value(
                "System Settings", "language")
    return get_all_translations(language)


def check_app_permission():
    if frappe.session.user == "Administrator":
        return True

    return False

@frappe.whitelist()
def get_posthog_settings():
	return {
		"posthog_project_id": frappe.conf.get(POSTHOG_PROJECT_FIELD),
		"posthog_host": frappe.conf.get(POSTHOG_HOST_FIELD),
		"enable_telemetry": frappe.get_system_settings("enable_telemetry"),
		"telemetry_site_age": frappe.utils.telemetry.site_age(),
	}

@frappe.whitelist()
def get_fields(doctype: str, allow_all_fieldtypes: bool = False):
	not_allowed_fieldtypes = list(frappe.model.no_value_fields) + ["Read Only"]
	if allow_all_fieldtypes:
		not_allowed_fieldtypes = []
	fields = frappe.get_meta(doctype).fields

	_fields = []

	for field in fields:
		if (
			field.fieldtype not in not_allowed_fieldtypes
			and field.fieldname
		):
			_fields.append({
				"label": field.label,
				"type": field.fieldtype,
				"value": field.fieldname,
				"options": field.options,
				"mandatory": field.reqd,
				"read_only": field.read_only,
				"hidden": field.hidden,
				"depends_on": field.depends_on,
				"mandatory_depends_on": field.mandatory_depends_on,
				"read_only_depends_on": field.read_only_depends_on,
				"link_filters": field.get("link_filters"),
				"placeholder": field.get("placeholder"),
			})

	return _fields

@frappe.whitelist()
def get_all_users():
	#frappe.only_for(["Moderator", "Course Creator", "Batch Evaluator"])
	users = frappe.get_all(
		"User",
		{
			"enabled": 1,
		},
		["name", "full_name", "user_image"],
	)

	return {user.name: user for user in users}

@frappe.whitelist(allow_guest=True)
def get_user_info():
	if frappe.session.user == "Guest":
		return None

	user = frappe.db.get_value(
		"User",
		frappe.session.user,
		["name", "email", "enabled", "user_image", "full_name", "user_type", "username"],
		as_dict=1,
	)
	user["roles"] = frappe.get_roles(user.name)
	
	user.is_system_manager = "System Manager" in user.roles
	if user.is_system_manager:
		user.sitename = frappe.local.site
	return user

@frappe.whitelist()
def get_job_position_rounds(job_position):
	try:
		job_doc = frappe.get_doc("ATS_Position", job_position)

		rounds = []
		for round in job_doc.job_position_rounds:
			# Parse triggers từ JSON string sang list (nếu có)
			triggers = []
			# if round.automation_rules:
			# 	try:
			# 		triggers = frappe.parse_json(round.automation_rules)
			# 	except Exception:
			# 		triggers = []

			rounds.append({
				"name": round.name,
				"round_name": round.round_name,
				"round_type": round.round_type,
				"position": round.position,
				"default": round.default,
				"triggers": triggers,
			})

		# Sắp xếp theo position
		rounds = sorted(rounds, key=lambda r: r["position"])

		# Phân chia theo cấu trúc
		if len(rounds) == 0:
			return {"success": True, "fixedStart": [], "draggableRounds": [], "fixedEnd": []}
		if len(rounds) == 1:
			return {"success": True, "fixedStart": [rounds[0]], "draggableRounds": [], "fixedEnd": []}
		if len(rounds) == 2:
			return {"success": True, "fixedStart": [rounds[0]], "draggableRounds": [], "fixedEnd": [rounds[1]]}
		if len(rounds) == 3:
			return {"success": True, "fixedStart": [rounds[0]], "draggableRounds": [], "fixedEnd": rounds[1:]}

		return {
			"success": True,
			"fixedStart": [rounds[0]],
			"draggableRounds": rounds[1:-2],
			"fixedEnd": rounds[-2:],
		}
	except Exception as e:
		frappe.log_error(f"Error getting job position rounds: {str(e)}")
		return {"success": False, "message": str(e)}