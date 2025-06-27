import frappe

@frappe.whitelist()
def get_site_config():
    """Get mbw_ats_site_name configuration"""
    try:
        site_config = frappe.get_site_config()
        mbw_ats_site_name = site_config.get("mbw_ats_site_name", "")
        return {
            "success": True,
            "mbw_ats_site_name": mbw_ats_site_name
        }
    except Exception as e:
        frappe.log_error(f"Error getting site config: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "mbw_ats_site_name": ""
        } 