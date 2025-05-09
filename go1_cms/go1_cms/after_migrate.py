from __future__ import unicode_literals, print_function

import frappe
import os
import re
import json
import zipfile
from frappe.utils import encode, get_files_path, getdate, to_timedelta,  flt


def after_migrate():
	"""
	Synchronize all ATS category data in the correct order
	First tier categories need to be synced first, then second tier, then third tier
	"""
	try:
		frappe.log_error("==Starting ATS categories synchronization", "after_migrate")
		
		# Import the sync_get_data module
		from go1_cms.api import sync_get_data
		
		# First tier categories (basic data)
		frappe.log_error("==Syncing first tier categories", "after_migrate")
		sync_get_data.sync_ats_company()
		sync_get_data.sync_ats_country()
		sync_get_data.sync_ats_province()
		sync_get_data.sync_ats_district()
		sync_get_data.sync_ats_ward()
		sync_get_data.sync_ats_round_type()
		sync_get_data.sync_ats_educationlevel()
		sync_get_data.sync_ats_institution()
		sync_get_data.sync_ats_major()
		
		# Second tier categories (depend on first tier)
		frappe.log_error("==Syncing second tier categories", "after_migrate")
		sync_get_data.sync_ats_unit()
		sync_get_data.sync_ats_profession()
		sync_get_data.sync_ats_level()
		sync_get_data.sync_ats_location()
		sync_get_data.sync_ats_position()
		sync_get_data.sync_ats_candidatesource()
		
		# Third tier categories (depend on second tier)
		frappe.log_error("==Syncing third tier categories", "after_migrate")
		sync_get_data.sync_job_position_rounds()
		sync_get_data.sync_ats_jobopening()
		
		# Child tables
		frappe.log_error("==Syncing child tables", "after_migrate")
		sync_get_data.sync_hiring_committee()
		sync_get_data.sync_candidate_certification()
		sync_get_data.sync_candidate_skill()
		sync_get_data.sync_candidate_award()
		sync_get_data.sync_candidate_course()
		sync_get_data.sync_candidate_stages()
		sync_get_data.sync_ats_candidateroundhistory()
		sync_get_data.sync_candidate_work_experience()
		sync_get_data.sync_candidate_project()
		
		frappe.log_error("==ATS categories synchronization completed", "after_migrate")
	except Exception as e:
		frappe.log_error(f"Error in ATS categories synchronization: {str(e)}", "after_migrate")
