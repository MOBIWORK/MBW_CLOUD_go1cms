import requests
import frappe
from frappe import _


def get_api_config(endpoint):
    
    # Base URL for the API
    api_base_url = "https://ivan-ats.mbwnext.com"
    api_url = f"{api_base_url}{endpoint}"
    headers = {
        "X-API-Key": frappe.conf.get("mbw_ats_api_key"),
        "X-API-Secret": frappe.conf.get("mbw_ats_api_secret")
    }
    
    return api_url, headers

@frappe.whitelist(allow_guest=True)
def sync_ats_company():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_companies"
        project_a_api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(project_a_api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        if response_data_message.get("status") == "success":
            companies = response_data_message.get("data", [])

            for company in companies:
                # Check if the record already exists in ATS_Company
                existing_company = frappe.db.exists("ATS_Company", {"company_id": company.get("company_id")})

                if existing_company:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Company", existing_company)
                    doc.update(company)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Company",
                        **company
                    })
                    doc.insert()

            frappe.db.commit()
            return "Company synchronization completed successfully."
        else:
            return f"Failed to fetch company data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_company Error")
        return f"An error occurred: {str(e)}"

# Danh mục đơn cần đồng bộ đầu tiên

@frappe.whitelist(allow_guest=True)
def sync_ats_country():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_countries"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            countries = response_data_message.get("data", [])

            for country in countries:
                # Check if the record already exists
                existing_country = frappe.db.exists("ATS_Country", {"country_id": country.get("country_id")})

                if existing_country:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Country", existing_country)
                    doc.update(country)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Country",
                        **country
                    })
                    doc.insert()

            frappe.db.commit()
            return "Country synchronization completed successfully."
        else:
            return f"Failed to fetch country data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_country Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_province():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_provinces"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            provinces = response_data_message.get("data", [])

            for province in provinces:
                # Check if the record already exists
                existing_province = frappe.db.exists("ATS_Province", {"province_id": province.get("province_id")})

                if existing_province:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Province", existing_province)
                    doc.update(province)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Province",
                        **province
                    })
                    doc.insert()

            frappe.db.commit()
            return "Province synchronization completed successfully."
        else:
            return f"Failed to fetch province data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_province Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_district():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_districts"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            districts = response_data_message.get("data", [])
            
            # Track processed district_ids to avoid duplicates
            processed_ids = set()
            
            for district in districts:
                district_id = district.get("district_id")
                
                # Skip if already processed in this batch
                if district_id in processed_ids:
                    continue
                
                processed_ids.add(district_id)
                
                # Check if the record already exists by district_id
                existing_district = frappe.db.exists("ATS_District", {"district_id": district_id})
                
                if existing_district:
                    # Update existing record
                    try:
                        doc = frappe.get_doc("ATS_District", existing_district)
                        
                        # Only update fields other than district_name to avoid unique constraint issues
                        for key, value in district.items():
                            if key != "district_name":
                                doc.set(key, value)
                                
                        doc.save()
                    except Exception as e:
                        frappe.log_error(f"Error updating district {district_id}", "sync_district_err")
                else:
                    # For new records, check if the name already exists
                    district_name = district.get("district_name")
                    name_exists = frappe.db.exists("ATS_District", {"district_name": district_name})
                    
                    if name_exists:
                        # If name exists, make it unique by adding district_id
                        district["district_name"] = f"{district_name} ({district_id})"
                    
                    # Insert new record
                    try:
                        doc = frappe.get_doc({
                            "doctype": "ATS_District",
                            **district
                        })
                        doc.insert()
                    except Exception as e:
                        frappe.log_error(f"Error inserting district {district_id}", "sync_district_err")

            frappe.db.commit()
            return "District synchronization completed successfully."
        else:
            return f"Failed to fetch district data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback()[:500], "sync_ats_district Error")
        return f"An error occurred: {str(e)[:100]}"

@frappe.whitelist(allow_guest=True)
def sync_ats_ward():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_wards"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            wards = response_data_message.get("data", [])

            for ward in wards:
                # Check if the record already exists
                existing_ward = frappe.db.exists("ATS_Ward", {"ward_id": ward.get("ward_id")})

                if existing_ward:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Ward", existing_ward)
                    doc.update(ward)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Ward",
                        **ward
                    })
                    doc.insert()

            frappe.db.commit()
            return "Ward synchronization completed successfully."
        else:
            return f"Failed to fetch ward data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_ward Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_round_type():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_round_types"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            round_types = response_data_message.get("data", [])

            for round_type in round_types:
                # Check if the record already exists
                existing_round_type = frappe.db.exists("ATS_Round_Type", {"round_type_name": round_type.get("round_type_name")})

                if existing_round_type:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Round_Type", existing_round_type)
                    doc.update(round_type)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Round_Type",
                        **round_type
                    })
                    doc.insert()

            frappe.db.commit()
            return "Round Type synchronization completed successfully."
        else:
            return f"Failed to fetch round type data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_round_type Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_educationlevel():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_education_levels"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            education_levels = response_data_message.get("data", [])

            for education_level in education_levels:
                # Check if the record already exists
                existing_education_level = frappe.db.exists("ATS_EducationLevel", {"educationlevel_id": education_level.get("educationlevel_id")})

                if existing_education_level:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_EducationLevel", existing_education_level)
                    doc.update(education_level)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_EducationLevel",
                        **education_level
                    })
                    doc.insert()

            frappe.db.commit()
            return "Education Level synchronization completed successfully."
        else:
            return f"Failed to fetch education level data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_educationlevel Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_institution():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_institutions"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            institutions = response_data_message.get("data", [])

            for institution in institutions:
                # Check if the record already exists
                existing_institution = frappe.db.exists("ATS_Institution", {"institution_id": institution.get("institution_id")})

                if existing_institution:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Institution", existing_institution)
                    doc.update(institution)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Institution",
                        **institution
                    })
                    doc.insert()

            frappe.db.commit()
            return "Institution synchronization completed successfully."
        else:
            return f"Failed to fetch institution data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_institution Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_major():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_majors"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            majors = response_data_message.get("data", [])

            for major in majors:
                # Check if the record already exists
                existing_major = frappe.db.exists("ATS_Major", {"major_id": major.get("major_id")})

                if existing_major:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Major", existing_major)
                    doc.update(major)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Major",
                        **major
                    })
                    doc.insert()

            frappe.db.commit()
            return "Major synchronization completed successfully."
        else:
            return f"Failed to fetch major data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_major Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_job_position_rounds():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_job_position_rounds"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            rounds = response_data_message.get("data", [])

            for round in rounds:
                # Check if the record already exists
                existing_round = frappe.db.exists("Job_Position_Rounds", {
                    "round_name": round.get("round_name"),
                    "parent": round.get("parent")
                })

                if existing_round:
                    # Update the existing record
                    doc = frappe.get_doc("Job_Position_Rounds", existing_round)
                    doc.update(round)
                    doc.save()
                else:
                    # Set parenttype for new records
                    round['parenttype'] = 'ATS_Position'
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "Job_Position_Rounds",
                        **round
                    })
                    doc.insert()

            frappe.db.commit()
            return "Job Position Rounds synchronization completed successfully."
        else:
            return f"Failed to fetch job position rounds data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_job_position_rounds Error")
        return f"An error occurred: {str(e)}"

# @frappe.whitelist(allow_guest=True)
# def sync_ats_rejectreasoncampaigngroup():
#     try:
#         # Get API URL and headers
#         endpoint = "/api/method/mbw_ats.api.sync_return_data.get_reject_reason_campaign_groups"
#         api_url, headers = get_api_config(endpoint)
        
#         # Fetch data from API
#         response = requests.get(api_url, headers=headers)
#         response_data = response.json()
#         response_data_message = response_data.get("message")
        
#         if response_data_message.get("status") == "success":
#             campaign_groups = response_data_message.get("data", [])

#             for rejectreasoncampaigngroup in campaign_groups:
#                 # Check if the record already exists
#                 existing_rejectreasoncampaigngroup = frappe.db.exists("ATS_RejectReasonCampaignGroup", {"rejectreasoncampaigngroup_id": rejectreasoncampaigngroup.get("rejectreasoncampaigngroup_id")})

#                 if existing_rejectreasoncampaigngroup:
#                     # Update the existing record
#                     doc = frappe.get_doc("ATS_RejectReasonCampaignGroup", existing_rejectreasoncampaigngroup)
#                     doc.update(rejectreasoncampaigngroup)
#                     doc.save()
#                 else:
#                     # Insert a new record
#                     doc = frappe.get_doc({
#                         "doctype": "ATS_RejectReasonCampaignGroup",
#                         **rejectreasoncampaigngroup
#                     })
#                     doc.insert()

#             frappe.db.commit()
#             return "Reject Reason Campaign Group synchronization completed successfully."
#         else:
#             return f"Failed to fetch reject reason campaign group data: {response_data_message.get('message')}"

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "sync_ats_rejectreasoncampaigngroup Error")
#         return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_hiring_committee():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_hiring_committees"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            committees = response_data_message.get("data", [])

            for committee in committees:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if committee.get("parent") and committee.get("parenttype") and committee.get("parentfield"):
                    parent_doc = frappe.get_doc(committee["parenttype"], committee["parent"])
                    
                    # Check if this committee member already exists in the parent
                    existing = False
                    for member in parent_doc.get(committee["parentfield"] or "hiring_committee", []):
                        if member.user == committee["user"]:
                            # Update existing member
                            member.notify_on_new_candidate = committee["notify_on_new_candidate"]
                            member.can_view_offer_letter_details = committee["can_view_offer_letter_details"]
                            existing = True
                            break
                    
                    # If not found, add new member
                    if not existing:
                        parent_doc.append(committee["parentfield"] or "hiring_committee", {
                            "user": committee["user"],
                            "notify_on_new_candidate": committee["notify_on_new_candidate"],
                            "can_view_offer_letter_details": committee["can_view_offer_letter_details"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Hiring Committee completed successfully."
        else:
            return f"Failed to fetch hiring committee data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_hiring_committee Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_candidate_certification():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_certifications"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            certifications = response_data_message.get("data", [])

            for certification in certifications:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if certification.get("parent") and certification.get("parenttype") and certification.get("parentfield"):
                    parent_doc = frappe.get_doc(certification["parenttype"], certification["parent"])
                    
                    # Check if this certification already exists in the parent
                    existing = False
                    for existing_cert in parent_doc.get(certification["parentfield"] or "candidate_certification", []):
                        if (existing_cert.can_cert_name == certification["can_cert_name"] and 
                            existing_cert.can_cert_organization == certification["can_cert_organization"] and
                            existing_cert.can_cert_issued_date == certification["can_cert_issued_date"]):
                            # Update existing certification
                            existing_cert.can_cert_expiration_date = certification["can_cert_expiration_date"]
                            existing_cert.can_cert_file = certification["can_cert_file"]
                            existing_cert.can_cert_link = certification["can_cert_link"]
                            existing = True
                            break
                    
                    # If not found, add new certification
                    if not existing:
                        parent_doc.append(certification["parentfield"] or "candidate_certification", {
                            "can_cert_name": certification["can_cert_name"],
                            "can_cert_organization": certification["can_cert_organization"],
                            "can_cert_issued_date": certification["can_cert_issued_date"],
                            "can_cert_expiration_date": certification["can_cert_expiration_date"],
                            "can_cert_file": certification["can_cert_file"],
                            "can_cert_link": certification["can_cert_link"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate_Certification completed successfully."
        else:
            return f"Failed to fetch candidate certification data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_certification Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_candidate_skill():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_skills"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            skills = response_data_message.get("data", [])

            for skill in skills:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if skill.get("parent") and skill.get("parenttype") and skill.get("parentfield"):
                    parent_doc = frappe.get_doc(skill["parenttype"], skill["parent"])
                    
                    # Check if this skill already exists in the parent
                    existing = False
                    for existing_skill in parent_doc.get(skill["parentfield"] or "candidate_skill", []):
                        if existing_skill.can_skill_name == skill["can_skill_name"]:
                            # Update existing skill
                            existing_skill.levels = skill["levels"]
                            existing_skill.descriptions = skill["descriptions"]
                            existing = True
                            break
                    
                    # If not found, add new skill
                    if not existing:
                        parent_doc.append(skill["parentfield"] or "candidate_skill", {
                            "can_skill_name": skill["can_skill_name"],
                            "levels": skill["levels"],
                            "descriptions": skill["descriptions"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate_Skill completed successfully."
        else:
            return f"Failed to fetch candidate skill data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_skill Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_candidate_award():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_awards"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            awards = response_data_message.get("data", [])

            for award in awards:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if award.get("parent") and award.get("parenttype") and award.get("parentfield"):
                    parent_doc = frappe.get_doc(award["parenttype"], award["parent"])
                    
                    # Check if this award already exists in the parent
                    existing = False
                    for existing_award in parent_doc.get(award["parentfield"] or "candidate_award", []):
                        if (existing_award.can_award_name == award["can_award_name"] and 
                            existing_award.can_award_organization == award["can_award_organization"] and
                            existing_award.can_award_received_date == award["can_award_received_date"]):
                            # Update existing award
                            existing_award.can_award_file = award["can_award_file"]
                            existing_award.can_award_link = award["can_award_link"]
                            existing = True
                            break
                    
                    # If not found, add new award
                    if not existing:
                        parent_doc.append(award["parentfield"] or "candidate_award", {
                            "can_award_name": award["can_award_name"],
                            "can_award_organization": award["can_award_organization"],
                            "can_award_received_date": award["can_award_received_date"],
                            "can_award_file": award["can_award_file"],
                            "can_award_link": award["can_award_link"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate_Award completed successfully."
        else:
            return f"Failed to fetch candidate award data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_award Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_candidate_course():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_courses"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            courses = response_data_message.get("data", [])

            for course in courses:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if course.get("parent") and course.get("parenttype") and course.get("parentfield"):
                    parent_doc = frappe.get_doc(course["parenttype"], course["parent"])
                    
                    # Check if this course already exists in the parent
                    existing = False
                    for existing_course in parent_doc.get(course["parentfield"] or "candidate_course", []):
                        if (existing_course.can_course_name == course["can_course_name"] and 
                            existing_course.can_course_organization == course["can_course_organization"] and
                            existing_course.can_course_start_date == course["can_course_start_date"]):
                            # Update existing course
                            existing_course.can_course_end_date = course["can_course_end_date"]
                            existing_course.can_course_details = course["can_course_details"]
                            existing_course.can_cert_file = course["can_cert_file"]
                            existing_course.can_cert_link = course["can_cert_link"]
                            existing = True
                            break
                    
                    # If not found, add new course
                    if not existing:
                        parent_doc.append(course["parentfield"] or "candidate_course", {
                            "can_course_name": course["can_course_name"],
                            "can_course_organization": course["can_course_organization"],
                            "can_course_start_date": course["can_course_start_date"],
                            "can_course_end_date": course["can_course_end_date"],
                            "can_course_details": course["can_course_details"],
                            "can_cert_file": course["can_cert_file"],
                            "can_cert_link": course["can_cert_link"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate_Course completed successfully."
        else:
            return f"Failed to fetch candidate course data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_course Error")
        return f"An error occurred: {str(e)}"

# Danh mục cần đồng bộ thứ hai
@frappe.whitelist()
def sync_ats_unit():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_ats_units"
        api_url, headers = get_api_config(endpoint)
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            units = response_data_message.get("data", [])
            frappe.log_error(f"Fetched {len(units)} units from API", "sync_ats_unit")
            
            # Trước tiên, đồng bộ tất cả các đơn vị, bỏ qua mối quan hệ parent
            # Sau đó, chúng ta sẽ cập nhật mối quan hệ parent sau
            
            # Đánh dấu các unit_id đã được xử lý
            processed_units = {}
            
            # Bước 1: Tạo hoặc cập nhật tất cả các đơn vị, không thiết lập parent_ats_unit
            for unit in units:
                unit_id = unit.get("unit_id")
                unit_name = unit.get("unit_name")
                
                # Lưu trữ thông tin parent để cập nhật sau
                parent_ats_unit = unit.get("parent_ats_unit")
                old_parent = unit.get("old_parent")
                
                # Tạm thời loại bỏ mối quan hệ parent để tránh lỗi
                temp_unit = unit.copy()
                temp_unit["parent_ats_unit"] = None
                temp_unit["old_parent"] = None
                
                try:
                    # Kiểm tra đơn vị đã tồn tại chưa
                    existing_unit = frappe.db.exists("ATS_Unit", {"unit_id": unit_id})
                    
                    if existing_unit:
                        # Cập nhật đơn vị đã tồn tại, không cập nhật parent
                        doc = frappe.get_doc("ATS_Unit", existing_unit)
                        
                        # Cập nhật các trường ngoại trừ parent_ats_unit và old_parent
                        for key, value in temp_unit.items():
                            if key not in ["parent_ats_unit", "old_parent"]:
                                doc.set(key, value)
                        
                        doc.save()
                        frappe.log_error(f"Updated unit {unit_name} ({unit_id}) without parent", "sync_ats_unit")
                    else:
                        # Tạo mới đơn vị
                        doc = frappe.get_doc({
                            "doctype": "ATS_Unit",
                            **temp_unit
                        })
                        doc.insert()
                        frappe.log_error(f"Created new unit {unit_name} ({unit_id}) without parent", "sync_ats_unit")
                    
                    # Lưu thông tin đơn vị và parent của nó để cập nhật sau
                    processed_units[unit_id] = {
                        "name": doc.name,
                        "unit_name": unit_name,
                        "parent_ats_unit": parent_ats_unit,
                        "old_parent": old_parent
                    }
                    
                except Exception as e:
                    frappe.log_error(f"Error in first pass for unit {unit_name} ({unit_id}): {str(e)}", "sync_ats_unit_error")
            
            # Bước 2: Cập nhật mối quan hệ parent cho tất cả các đơn vị
            for unit_id, unit_info in processed_units.items():
                parent_name = unit_info.get("parent_ats_unit")
                old_parent_name = unit_info.get("old_parent")
                
                # Bỏ qua nếu không có parent
                if not parent_name and not old_parent_name:
                    continue
                
                try:
                    # Lấy doc của đơn vị hiện tại
                    doc = frappe.get_doc("ATS_Unit", unit_info.get("name"))
                    
                    # Cập nhật parent_ats_unit nếu có
                    if parent_name:
                        # Tìm parent unit trong cơ sở dữ liệu
                        parent_doc = frappe.db.get_value("ATS_Unit", {"unit_name": parent_name}, "name")
                        if parent_doc:
                            doc.parent_ats_unit = parent_doc
                            frappe.log_error(f"Updated parent for {unit_info.get('unit_name')}: {parent_name} -> {parent_doc}", "sync_ats_unit")
                        else:
                            frappe.log_error(f"Parent unit {parent_name} not found for {unit_info.get('unit_name')}", "sync_ats_unit_error")
                    
                    # Cập nhật old_parent nếu có
                    if old_parent_name:
                        # Tìm old parent unit trong cơ sở dữ liệu
                        old_parent_doc = frappe.db.get_value("ATS_Unit", {"unit_name": old_parent_name}, "name")
                        if old_parent_doc:
                            doc.old_parent = old_parent_doc
                            frappe.log_error(f"Updated old_parent for {unit_info.get('unit_name')}: {old_parent_name} -> {old_parent_doc}", "sync_ats_unit")
                        else:
                            frappe.log_error(f"Old parent unit {old_parent_name} not found for {unit_info.get('unit_name')}", "sync_ats_unit_error")
                    
                    # Lưu thay đổi
                    doc.save()
                    
                except Exception as e:
                    frappe.log_error(f"Error updating parent for {unit_info.get('unit_name')}: {str(e)}", "sync_ats_unit_error")
            
            frappe.db.commit()
            return "Unit synchronization completed successfully."
        else:
            return f"Failed to fetch unit data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_unit Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_profession():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_ats_professions"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        if response_data_message.get("status") == "success":
            professions = response_data_message.get("data", [])

            for profession in professions:
                # Check if the record already exists
                existing_profession = frappe.db.exists("ATS_Profession", {"profession_id": profession.get("profession_id")})

                if existing_profession:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Profession", existing_profession)
                    doc.update(profession)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Profession",
                        **profession
                    })
                    doc.insert()

            frappe.db.commit()
            return "Profession synchronization completed successfully."
        else:
            return f"Failed to fetch profession data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_profession Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_level():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_ats_levels"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            levels = response_data_message.get("data", [])

            for level in levels:
                # Check if the record already exists
                existing_level = frappe.db.exists("ATS_Level", {"level_id": level.get("level_id")})

                if existing_level:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Level", existing_level)
                    doc.update(level)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Level",
                        **level
                    })
                    doc.insert()

            frappe.db.commit()
            return "Level synchronization completed successfully."
        else:
            return f"Failed to fetch level data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_level Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_location():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_ats_locations"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            locations = response_data_message.get("data", [])

            for location in locations:
                # Check if the record already exists
                existing_location = frappe.db.exists("ATS_Location", {"location_id": location.get("location_id")})

                if existing_location:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Location", existing_location)
                    doc.update(location)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Location",
                        **location
                    })
                    doc.insert()

            frappe.db.commit()
            return "Location synchronization completed successfully."
        else:
            return f"Failed to fetch location data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_location Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_position():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_positions"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            positions = response_data_message.get("data", [])

            for position in positions:
                # Check if the record already exists
                existing_position = frappe.db.exists("ATS_Position", {"position_id": position.get("position_id")})

                if existing_position:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Position", existing_position)
                    doc.update(position)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Position",
                        **position
                    })
                    doc.insert()

            frappe.db.commit()
            return "Position synchronization completed successfully."
        else:
            return f"Failed to fetch position data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_position Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_candidatesource():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_sources"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            candidate_sources = response_data_message.get("data", [])

            for candidatesource in candidate_sources:
                # Check if the record already exists
                existing_candidatesource = frappe.db.exists("ATS_CandidateSource", {"candidatesource_id": candidatesource.get("candidatesource_id")})

                if existing_candidatesource:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_CandidateSource", existing_candidatesource)
                    doc.update(candidatesource)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_CandidateSource",
                        **candidatesource
                    })
                    doc.insert()

            frappe.db.commit()
            return "Candidate Source synchronization completed successfully."
        else:
            return f"Failed to fetch candidate source data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_candidatesource Error")
        return f"An error occurred: {str(e)}"

# @frappe.whitelist(allow_guest=True)
# def sync_ats_rejectreasoncampaign():
#     try:
#         # Get API URL and headers
#         endpoint = "/api/method/mbw_ats.api.sync_return_data.get_reject_reason_campaigns"
#         api_url, headers = get_api_config(endpoint)
        
#         # Fetch data from API
#         response = requests.get(api_url, headers=headers)
#         response_data = response.json()
#         response_data_message = response_data.get("message")
        
#         if response_data_message.get("status") == "success":
#             reject_reason_campaigns = response_data_message.get("data", [])

#             for rejectreasoncampaign in reject_reason_campaigns:
#                 # Check if the record already exists
#                 existing_rejectreasoncampaign = frappe.db.exists("ATS_RejectReasonCampaign", {"rejectreasoncampaign_id": rejectreasoncampaign.get("rejectreasoncampaign_id")})

#                 if existing_rejectreasoncampaign:
#                     # Update the existing record
#                     doc = frappe.get_doc("ATS_RejectReasonCampaign", existing_rejectreasoncampaign)
#                     doc.update(rejectreasoncampaign)
#                     doc.save()
#                 else:
#                     # Insert a new record
#                     doc = frappe.get_doc({
#                         "doctype": "ATS_RejectReasonCampaign",
#                         **rejectreasoncampaign
#                     })
#                     doc.insert()

#             frappe.db.commit()
#             return "Reject Reason Campaign synchronization completed successfully."
#         else:
#             return f"Failed to fetch reject reason campaign data: {response_data_message.get('message')}"

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "sync_ats_rejectreasoncampaign Error")
#         return f"An error occurred: {str(e)}"

# @frappe.whitelist(allow_guest=True)
# def sync_ats_rejectreason():
#     try:
#         # Get API URL and headers
#         endpoint = "/api/method/mbw_ats.api.sync_return_data.get_reject_reasons"
#         api_url, headers = get_api_config(endpoint)
        
#         # Fetch data from API
#         response = requests.get(api_url, headers=headers)
#         response_data = response.json()
#         response_data_message = response_data.get("message")
        
#         if response_data_message.get("status") == "success":
#             reject_reasons = response_data_message.get("data", [])

#             for rejectreason in reject_reasons:
#                 # Check if the record already exists
#                 existing_rejectreason = frappe.db.exists("ATS_RejectReason", {"rejectionreason_id": rejectreason.get("rejectionreason_id")})

#                 if existing_rejectreason:
#                     # Update the existing record
#                     doc = frappe.get_doc("ATS_RejectReason", existing_rejectreason)
#                     doc.update(rejectreason)
#                     doc.save()
#                 else:
#                     # Insert a new record
#                     doc = frappe.get_doc({
#                         "doctype": "ATS_RejectReason",
#                         **rejectreason
#                     })
#                     doc.insert()

#             frappe.db.commit()
#             return "Reject Reason synchronization completed successfully."
#         else:
#             return f"Failed to fetch reject reason data: {response_data_message.get('message')}"

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "sync_ats_rejectreason Error")
#         return f"An error occurred: {str(e)}"

# Danh Mục cần đồng bộ thứ ba
@frappe.whitelist(allow_guest=True)
def sync_ats_jobopening():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_ats_jobopenings"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            job_openings = response_data_message.get("data", [])

            for jobopening in job_openings:
                # Check if the record already exists
                existing_jobopening = frappe.db.exists("ATS_JobOpening", {"jo_id": jobopening.get("jo_id")})

                if existing_jobopening:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_JobOpening", existing_jobopening)
                    doc.update(jobopening)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_JobOpening",
                        **jobopening
                    })
                    doc.insert()

            frappe.db.commit()
            return "Job Opening synchronization completed successfully."
        else:
            return f"Failed to fetch job opening data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_jobopening Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_candidate():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_ats_candidates"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            candidates = response_data_message.get("data", [])
            for candidate in candidates:
                print("Test log candidate : >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",candidates)
                # Check if the record already exists
                existing_candidate = frappe.db.exists("ATS_Candidate", {"can_id": candidate.get("can_id")})

                if existing_candidate:
                    # Update the existing record
                    doc = frappe.get_doc("ATS_Candidate", existing_candidate)
                    doc.update(candidate)
                    doc.save()
                else:
                    # Insert a new record
                    doc = frappe.get_doc({
                        "doctype": "ATS_Candidate",
                        **candidate
                    })
                    doc.insert()

            frappe.db.commit()
            return "Candidate synchronization completed successfully."
        else:
            return f"Failed to fetch candidate data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_candidate Error")
        return f"An error occurred: {str(e)}"


@frappe.whitelist(allow_guest=True)
def sync_candidate_stages():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_stages"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            stages = response_data_message.get("data", [])

            for stage in stages:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if stage.get("parent") and stage.get("parenttype") and stage.get("parentfield"):
                    parent_doc = frappe.get_doc(stage["parenttype"], stage["parent"])
                    
                    # Check if this stage already exists in the parent
                    existing = False
                    for existing_stage in parent_doc.get(stage["parentfield"] or "candidate_stages", []):
                        if (existing_stage.job_opening == stage["job_opening"] and 
                            existing_stage.status == stage["status"]):
                            # Update existing stage
                            existing_stage.rejected = stage["rejected"]
                            existing = True
                            break
                    
                    # If not found, add new stage
                    if not existing:
                        parent_doc.append(stage["parentfield"] or "candidate_stages", {
                            "job_opening": stage["job_opening"],
                            "status": stage["status"],
                            "rejected": stage["rejected"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate Stages completed successfully."
        else:
            return f"Failed to fetch candidate stages data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_stages Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_ats_candidateroundhistory():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_round_histories"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            round_histories = response_data_message.get("data", [])

            for round_history in round_histories:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if round_history.get("parent") and round_history.get("parenttype") and round_history.get("parentfield"):
                    parent_doc = frappe.get_doc(round_history["parenttype"], round_history["parent"])
                    
                    # Check if this round history already exists in the parent
                    existing = False
                    for existing_history in parent_doc.get(round_history["parentfield"] or "round_history", []):
                        if (existing_history.round_name == round_history["round_name"] and 
                            existing_history.change_date == round_history["change_date"]):
                            # Already exists, no need to update as it's historical data
                            existing = True
                            break
                    
                    # If not found, add new round history
                    if not existing:
                        parent_doc.append(round_history["parentfield"] or "round_history", {
                            "round_name": round_history["round_name"],
                            "change_date": round_history["change_date"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of ATS_CandidateRoundHistory completed successfully."
        else:
            return f"Failed to fetch candidate round history data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_ats_candidateroundhistory Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_candidate_work_experience():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_work_experiences"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            work_experiences = response_data_message.get("data", [])

            for work_experience in work_experiences:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if work_experience.get("parent") and work_experience.get("parenttype") and work_experience.get("parentfield"):
                    parent_doc = frappe.get_doc(work_experience["parenttype"], work_experience["parent"])
                    
                    # Check if this work experience already exists in the parent
                    existing = False
                    for existing_work_exp in parent_doc.get(work_experience["parentfield"] or "candidate_work_experience", []):
                        if (existing_work_exp.work_experience_place == work_experience["work_experience_place"] and 
                            existing_work_exp.work_experience_role == work_experience["work_experience_role"] and
                            existing_work_exp.work_experience_start == work_experience["work_experience_start"]):
                            # Update existing work experience
                            existing_work_exp.work_experience_end = work_experience["work_experience_end"]
                            existing_work_exp.work_experience_detail = work_experience["work_experience_detail"]
                            existing = True
                            break
                    
                    # If not found, add new work experience
                    if not existing:
                        parent_doc.append(work_experience["parentfield"] or "candidate_work_experience", {
                            "work_experience_place": work_experience["work_experience_place"],
                            "work_experience_role": work_experience["work_experience_role"],
                            "work_experience_start": work_experience["work_experience_start"],
                            "work_experience_end": work_experience["work_experience_end"],
                            "work_experience_detail": work_experience["work_experience_detail"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate_Work_Experience completed successfully."
        else:
            return f"Failed to fetch candidate work experience data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_work_experience Error")
        return f"An error occurred: {str(e)}"

@frappe.whitelist(allow_guest=True)
def sync_candidate_project():
    try:
        # Get API URL and headers
        endpoint = "/api/method/mbw_ats.api.sync_return_data.get_candidate_projects"
        api_url, headers = get_api_config(endpoint)
        
        # Fetch data from API
        response = requests.get(api_url, headers=headers)
        response_data = response.json()
        response_data_message = response_data.get("message")
        
        if response_data_message.get("status") == "success":
            projects = response_data_message.get("data", [])

            for project in projects:
                # Since this is a child table, we need to handle it differently
                # We'll check if the parent record exists first
                if project.get("parent") and project.get("parenttype") and project.get("parentfield"):
                    parent_doc = frappe.get_doc(project["parenttype"], project["parent"])
                    
                    # Check if this project already exists in the parent
                    existing = False
                    for existing_project in parent_doc.get(project["parentfield"] or "candidate_project", []):
                        if (existing_project.project_name == project["project_name"] and 
                            existing_project.project_start_date == project["project_start_date"]):
                            # Update existing project
                            existing_project.project_role = project["project_role"]
                            existing_project.project_end_date = project["project_end_date"]
                            existing_project.project_description = project["project_description"]
                            existing = True
                            break
                    
                    # If not found, add new project
                    if not existing:
                        parent_doc.append(project["parentfield"] or "candidate_project", {
                            "project_name": project["project_name"],
                            "project_role": project["project_role"],
                            "project_start_date": project["project_start_date"],
                            "project_end_date": project["project_end_date"],
                            "project_description": project["project_description"]
                        })
                    
                    parent_doc.save()

            frappe.db.commit()
            return "Synchronization of Candidate_Project completed successfully."
        else:
            return f"Failed to fetch candidate project data: {response_data_message.get('message')}"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "sync_candidate_project Error")
        return f"An error occurred: {str(e)}"


