import frappe
from hrms.hr.doctype.job_opening.job_opening import JobOpening


class CustomJobOpening(JobOpening):
    website = frappe._dict(
        template="go1_cms/templates/generators/job_opening.html",
        condition_field="publish",
        page_title_field="job_title",
    )

    def validate(self):
        if not self.route or not self.route.startswith('tuyen-dung/'):
            self.route = f"tuyen-dung/{frappe.scrub(self.job_title).replace('_', '-')}"

        super().validate()

    def get_context(self, context):
        context.doc_name = self.name
        context.meta_title = self.job_title
        
        # Safely get cms meta fields using getattr to avoid AttributeError
        cms_meta_description = getattr(self, 'cms_meta_description', None) or ''
        cms_meta_keywords = getattr(self, 'cms_meta_keywords', None) or ''
        cms_meta_title = getattr(self, 'cms_meta_title', None) or ''
        cms_meta_image = getattr(self, 'cms_meta_image', None) or ''
        
        context.metatags = frappe._dict({
            "description": cms_meta_description,
            "keywords": cms_meta_keywords,
            "og:title": cms_meta_title,
            "og:description": cms_meta_description,
            "og:image": cms_meta_image,
        })

        if not self.route.endswith('jobs-123-jobs-456-jobs'):
            web_client = frappe.db.get_value(
                'MBW Client Website', {"type_web": "Live version"}, pluck='name', as_dict=1)
            if web_client:
                web_item = frappe.db.get_value('MBW Client Website Item', {
                    'parent': web_client, 'parentfield': 'page_websites', 'page_type': 'Trang chi tiết tuyển dụng'}, ['page_id'], as_dict=1)

                if web_item and frappe.db.exists('Web Page Builder', web_item.page_id, cache=True):
                    doc_wpb = frappe.get_doc(
                        'Web Page Builder', web_item.page_id)
                    doc_wpb.get_context(context)
        else:
            web_test = frappe.db.exists('Web Page Builder', {
                'route': 'jobs-123-jobs-456-jobs'}, cache=True)
            if web_test:
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', web_test)
                doc_wpb.get_context(context)

        super().get_context(context)
