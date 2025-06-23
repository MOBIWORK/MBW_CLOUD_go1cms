# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
import time


class MBWWebsiteTemplate(Document):
    def before_naming(self):
        if not self.custom_name:
            self.custom_name = "WT-{}".format(getStrTimestamp())

    def validate(self):
        # Fix options fields that might be stored as list instead of string
        self.fix_select_field_options()
        
        if self.template_in_use == 1:
            existing_list = frappe.db.sql(
                '''UPDATE `tabMBW Website Template` SET template_in_use=0 WHERE name!="{web_name}" AND template_in_use=1'''.format(web_name=self.name))
            frappe.db.commit()

    def fix_select_field_options(self):
        """Fix select field options that might be stored as list instead of string"""
        try:
            # Get meta to check for select fields
            meta = frappe.get_meta(self.doctype)
            
            for df in meta.fields:
                if df.fieldtype == 'Select' and df.options:
                    field_value = getattr(self, df.fieldname, None)
                    
                    # Check if options is stored as list and convert to string
                    if isinstance(df.options, list):
                        df.options = '\n'.join(str(opt) for opt in df.options)
                        frappe.log_error(
                            title=f"Fixed options field: {df.fieldname}",
                            message=f"Converted list options to string for field {df.fieldname} in {self.doctype}"
                        )
                        
            # Also check child table fields
            for table_field in meta.get_table_fields():
                child_meta = frappe.get_meta(table_field.options)
                for child_df in child_meta.fields:
                    if child_df.fieldtype == 'Select' and child_df.options:
                        if isinstance(child_df.options, list):
                            child_df.options = '\n'.join(str(opt) for opt in child_df.options)
                            frappe.log_error(
                                title=f"Fixed child options field: {child_df.fieldname}",
                                message=f"Converted list options to string for field {child_df.fieldname} in {child_meta.name}"
                            )
                            
        except Exception as e:
            frappe.log_error(
                title="Error in fix_select_field_options",
                message=f"Error: {str(e)}\n{frappe.get_traceback()}"
            )

    @staticmethod
    def default_list_data():
        columns = []

        rows = [
            "name",
            "creation",
            "modified_by",
            "modified",
            "owner",
            "image_preview",
            "template_name",
            "template_in_use",
            "installed_template"
        ]
        return {'columns': columns, 'rows': rows}


def getStrTimestamp():
    arr_time = str(time.time()).split('.')
    while (len(arr_time[1]) < 7):
        arr_time[1] += '0'

    return arr_time[0] + arr_time[1]
