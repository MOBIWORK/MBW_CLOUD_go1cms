import frappe


@frappe.whitelist()
def get_users():
    users = frappe.qb.get_query(
        "User",
        fields=["name", "email", "enabled", "user_image",
                "first_name", "last_name", "full_name", "user_type"],
        order_by="full_name asc",
        distinct=True,
    ).run(as_dict=1)

    for user in users:
        if frappe.session.user == user.name:
            user.session_user = True

        user.is_manager = (
            "Sales Manager" in frappe.get_roles(
                user.name) or user.name == "Administrator"
        )
    return users
