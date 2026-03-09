import asyncio
import os
import sys

# Add backend directory to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import send_approval_credentials_email
from app.core.config import settings

def main():
    print("--- SpacePoint SMTP Test ---")
    print(f"Using SMTP_HOST: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"Using SMTP_USER: {settings.SMTP_USER}")
    
    if len(sys.argv) > 1:
        test_email = sys.argv[1]
    else:
        test_email = input("Enter an email address to send the test to: ").strip()
        
    if not test_email:
        print("No email provided. Exiting.")
        return
        
    print(f"\nAttempting to send an approval credentials email to {test_email}...")
    
    success = send_approval_credentials_email(
        to_email=test_email,
        name="Test Applicant",
        temp_password="TestPassword123!"
    )
    
    if success:
        print("\n✅ Success! The email was sent without raising an exception.")
        print("Please check the inbox (and spam folder) of the destination email.")
    else:
        print("\n❌ Failed! The email could not be sent. Please check your SMTP credentials in .env and ensure you are using an App Password if using Gmail.")

if __name__ == "__main__":
    main()
