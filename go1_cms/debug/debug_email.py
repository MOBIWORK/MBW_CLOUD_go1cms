#!/usr/bin/env python3

# Run this as: cd cms_fix && bench --site cms_fix execute debug_email.py

import frappe
from go1_cms.api.candidate_auth import invite_candidate

def debug_email_settings():
    """Debug email configuration"""
    print("=== EMAIL DEBUG ===")
    
    # 1. Check Email Account
    try:
        email_accounts = frappe.get_all(
            "Email Account", 
            fields=["name", "email_id", "enable_outgoing", "default_outgoing"]
        )
        print(f"Email Accounts: {email_accounts}")
    except Exception as e:
        print(f"Error getting email accounts: {str(e)}")
    
    # 2. Check default outgoing
    try:
        default_outgoing = frappe.db.get_single_value("Email Account", "default_outgoing")
        print(f"Default outgoing: {default_outgoing}")
    except Exception as e:
        print(f"Error getting default outgoing: {str(e)}")
    
    # 3. Test simple sendmail
    try:
        print("Testing simple sendmail...")
        frappe.sendmail(
            recipients="test@example.com",
            subject="Test Email",
            message="<p>Test email from debug script</p>",
            now=True
        )
        print("✅ Sendmail executed successfully")
    except Exception as e:
        print(f"❌ Sendmail error: {str(e)}")
        import traceback
        print(traceback.format_exc())

def test_invite_candidate_direct():
    """Test invite_candidate function directly"""
    print("\n=== INVITE CANDIDATE TEST ===")
    
    test_email = "trancongminh98it@gmail.com"
    test_name = "Test Candidate Direct"
    
    # Cleanup existing user first
    try:
        existing = frappe.db.exists("User", {"email": test_email})
        if existing:
            frappe.delete_doc("User", existing, force=True)
            frappe.db.commit()
            print(f"Deleted existing user: {existing}")
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
    
    # Test invite_candidate
    try:
        print(f"Calling invite_candidate({test_email}, {test_name})")
        result = invite_candidate(test_email, test_name)
        print(f"Result: {result}")
        
        # Check if user was created
        created_user = frappe.db.exists("User", {"email": test_email})
        print(f"User created: {created_user}")
        
        if created_user:
            user_doc = frappe.get_doc("User", created_user)
            print(f"User enabled: {user_doc.enabled}")
            print(f"Reset key exists: {bool(user_doc.reset_password_key)}")
        
    except Exception as e:
        print(f"❌ Error in invite_candidate: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    debug_email_settings()
    test_invite_candidate_direct() 