import frappe
from go1_cms.api.website.jobs import get_all_job

@frappe.whitelist(allow_guest=True)
def test_get_all_job_fixed():
    """
    Test hàm get_all_job sau khi sửa lỗi AttributeError cms_meta_description
    """
    try:
        # Test với section name không tồn tại (để test fallback)
        result = get_all_job('test_section_not_exist')
        
        data_count = len(result.get('data', []))
        debug_info = result.get('debug', {})
        pagination = result.get('pagination', {})
        
        return {
            "success": True,
            "message": "Hàm get_all_job hoạt động bình thường, không còn lỗi AttributeError",
            "test_results": {
                "data_count": data_count,
                "total_in_db": debug_info.get('total_records_in_db', 0),
                "published_records": debug_info.get('published_records', 0),
                "sort_field": debug_info.get('sort_field', ''),
                "pagination": pagination
            },
            "sample_data": result.get('data', [])[:2] if result.get('data') else []  # Chỉ lấy 2 record đầu
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "Vẫn còn lỗi trong hàm get_all_job"
        } 