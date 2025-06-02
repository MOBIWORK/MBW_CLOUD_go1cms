from __future__ import unicode_literals, print_function
import frappe
import os
import re
import json
import zipfile
from frappe.utils import encode, get_files_path, getdate, to_timedelta, flt
from go1_cms.api.sync_setup import sync_from_external


def after_migrate():
    try:
        sync_from_external("ATS_Company")
        sync_from_external("ATS_Unit")
        sync_from_external("ATS_Level")
        sync_from_external("ATS_Location")
        sync_from_external("ATS_Province")
        sync_from_external("ATS_Country")
        sync_from_external("ATS_Ward")
        sync_from_external("ATS_EducationLevel")
        sync_from_external("ATS_Education")
        sync_from_external("ATS_Institution")
        sync_from_external("ATS_Major")
        sync_from_external("ATS_Recruitment_Process")
        sync_from_external("ATS_Round_Type")
        sync_from_external("ATS_CandidateSource")
        sync_from_external("ATS_RejectReasonCampaignGroup")
        sync_from_external("Hiring Committee")
        sync_from_external("Hiring_Committee_Schedule")
        sync_from_external("Job_Opening_Rounds")
        sync_from_external("Job_Position_Rounds")
        sync_from_external("Candidate_Award")
        sync_from_external("Candidate_Certification")
        sync_from_external("Candidate_Project")
        sync_from_external("Candidate_Course")
        sync_from_external("Candidate_Skill")
        sync_from_external("Candidate_Work_Experience")
        sync_from_external("ATS_CandidateRoundHistory")
        sync_from_external("Candidate Stages")
        sync_from_external("ATS_JobOpening")

    except Exception as e:
        frappe.log_error("Error sync from get ", frappe.get_traceback())
