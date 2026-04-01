import os
import sys
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

from src.email_service import send_impact_report

def run_test():
    provider = os.getenv("EMAIL_PROVIDER", "SENDGRID").upper()
    print("=======================================")
    print(f"[TEST] Email Delivery Test (via {provider})")
    print("=======================================\n")
    
    recipient = os.getenv("GOVERNANCE_RECIPIENT")
    print(f"Loaded GOVERNANCE_RECIPIENT: {recipient}\n")
    
    if provider == "SENDGRID":
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL")
        print(f"Loaded SENDGRID_API_KEY: {'[SET]' if api_key and api_key != 'YOUR_SENDGRID_KEY_HERE' else '[MISSING or DEFAULT]'}")
        print(f"Loaded SENDGRID_FROM_EMAIL: {from_email}\n")
    else:
        smtp_server = os.getenv("SMTP_SERVER")
        print(f"Loaded SMTP_SERVER: {smtp_server}\n")
        
    print(f"Attempting to dispatch a mock email via {provider} to {recipient}...")
    
    # We will send a mock payload instead of a real excel file for this test
    # Or just pass None to test the raw connectivity and plain text mapping
    try:
        success, message = send_impact_report(
            recipient_email=recipient,
            attachment_data=None, 
            attachment_filename="Test_Report.xlsx"
        )
        
        if success:
            print("\n[SUCCESS]: " + message)
            print("Check your inbox to verify receipt!")
        else:
            print("\n[FAILED API/SMTP]: " + message)
            print("Please verify your specific provider configuration inside .env")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE]: The email_service crashed: {e}")

if __name__ == "__main__":
    run_test()
