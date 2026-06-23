import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("[TEST] Starting End-to-End Onboarding Assessment Flow Test via real HTTP requests...")
    
    # 1. Admin login
    print("[TEST] 1. Admin login...")
    admin_login_data = json.dumps({"email": "admin@spacepoint.com", "password": "admin"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=admin_login_data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    admin_cookie = None
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Admin login failed: {res.status}"
            headers = res.info()
            cookie_headers = headers.get_all("Set-Cookie")
            if cookie_headers:
                for c in cookie_headers:
                    if "access_token=" in c:
                        admin_cookie = c.split(";")[0]
            print(f"[TEST] Admin logged in. Cookie: {admin_cookie}")
    except Exception as e:
        print(f"[FAIL] Admin login failed with error: {e}")
        sys.exit(1)
        
    assert admin_cookie is not None, "Failed to get admin cookie"

    # 2. Admin sets status to RESEARCH_APPROVED for Lynn Faour (user ID 10)
    print("[TEST] 2. Setting status to RESEARCH_APPROVED...")
    review_data = json.dumps({
        "status": "RESEARCH_APPROVED",
        "feedback": "Approved research modules. Transitioning to 10 Questions Assessment."
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/admin/applicants/10/review", data=review_data, method="PUT")
    req.add_header("Content-Type", "application/json")
    req.add_header("Cookie", admin_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Status update to RESEARCH_APPROVED failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            print(f"[TEST] Admin review updated: {body}")
    except Exception as e:
        print(f"[FAIL] Transition to RESEARCH_APPROVED failed: {e}")
        sys.exit(1)

    # 3. Applicant (Lynn Faour) logs in
    print("[TEST] 3. Applicant login...")
    app_login_data = json.dumps({"email": "test2@gmail.com", "password": "password123"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=app_login_data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    app_cookie = None
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Applicant login failed: {res.status}"
            headers = res.info()
            cookie_headers = headers.get_all("Set-Cookie")
            if cookie_headers:
                for c in cookie_headers:
                    if "access_token=" in c:
                        app_cookie = c.split(";")[0]
            print(f"[TEST] Applicant logged in. Cookie: {app_cookie}")
    except Exception as e:
        print(f"[FAIL] Applicant login failed: {e}")
        sys.exit(1)
        
    assert app_cookie is not None, "Failed to get applicant cookie"

    # 4. Applicant checks status and retrieves questions
    print("[TEST] 4. Retrieve status and questions...")
    req = urllib.request.Request(f"{BASE_URL}/api/applicant/status", method="GET")
    req.add_header("Cookie", app_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Get status failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            assert body["status"] == "RESEARCH_APPROVED", f"Expected status RESEARCH_APPROVED, got {body['status']}"
            print(f"[TEST] Confirmed status is {body['status']}")
    except Exception as e:
        print(f"[FAIL] Checking status failed: {e}")
        sys.exit(1)

    req = urllib.request.Request(f"{BASE_URL}/api/applicant/assessment/questions", method="GET")
    req.add_header("Cookie", app_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Get questions failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            assert len(body) == 10, f"Expected 10 questions, got {len(body)}"
            print(f"[TEST] Fetched 10 questions successfully.")
    except Exception as e:
        print(f"[FAIL] Fetching questions failed: {e}")
        sys.exit(1)

    # 5. Applicant submits the assessment
    print("[TEST] 5. Submit assessment...")
    submit_form_data = urllib.parse.urlencode({
        "google_drive_link": "https://drive.google.com/drive/folders/test-assessment-folder-12345",
        "comments": "This is my completed onboarding assessment for SpacePoint. Verification comment."
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/applicant/assessment/submit", data=submit_form_data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Cookie", app_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Assessment submission failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            print(f"[TEST] Submission response: {body}")
    except Exception as e:
        print(f"[FAIL] Assessment submission failed: {e}")
        sys.exit(1)

    # 6. Verify applicant status has returned to UNDER_REVIEW
    print("[TEST] 6. Verify status changed back to UNDER_REVIEW...")
    req = urllib.request.Request(f"{BASE_URL}/api/applicant/status", method="GET")
    req.add_header("Cookie", app_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Get status failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            assert body["status"] == "UNDER_REVIEW", f"Expected UNDER_REVIEW, got {body['status']}"
            assert body["assessment"]["google_drive_link"] == "https://drive.google.com/drive/folders/test-assessment-folder-12345"
            assert "Verification comment" in body["assessment"]["comments"]
            print(f"[TEST] Confirmed status returned to {body['status']} and details are correct.")
    except Exception as e:
        print(f"[FAIL] Verifying status back to UNDER_REVIEW failed: {e}")
        sys.exit(1)

    # 7. Admin views submission details
    print("[TEST] 7. Admin checks submission details...")
    req = urllib.request.Request(f"{BASE_URL}/api/admin/applicants/10", method="GET")
    req.add_header("Cookie", admin_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Admin get applicant details failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            assert body["assessment"] is not None, "Expected assessment submission to be present"
            assert body["assessment"]["google_drive_link"] == "https://drive.google.com/drive/folders/test-assessment-folder-12345"
            assert "Verification comment" in body["assessment"]["comments"]
            print(f"[TEST] Admin successfully verified details in API.")
    except Exception as e:
        print(f"[FAIL] Admin verification of assessment details failed: {e}")
        sys.exit(1)

    # 8. Admin approves Phase 1 (moving status to PHASE_1_APPROVED)
    print("[TEST] 8. Set status to PHASE_1_APPROVED...")
    review_data2 = json.dumps({
        "status": "PHASE_1_APPROVED",
        "feedback": "Assessment looks perfect! Approved Phase 1."
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/admin/applicants/10/review", data=review_data2, method="PUT")
    req.add_header("Content-Type", "application/json")
    req.add_header("Cookie", admin_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Status update to PHASE_1_APPROVED failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            print(f"[TEST] Admin review updated: {body}")
    except Exception as e:
        print(f"[FAIL] Transition to PHASE_1_APPROVED failed: {e}")
        sys.exit(1)

    # 9. Verify applicant status is now PHASE_1_APPROVED
    print("[TEST] 9. Verify status is PHASE_1_APPROVED on applicant side...")
    req = urllib.request.Request(f"{BASE_URL}/api/applicant/status", method="GET")
    req.add_header("Cookie", app_cookie)
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200, f"Get status failed: {res.status}"
            body = json.loads(res.read().decode('utf-8'))
            assert body["status"] == "PHASE_1_APPROVED", f"Expected PHASE_1_APPROVED, got {body['status']}"
            print("[TEST] Checked and verified status is now PHASE_1_APPROVED.")
    except Exception as e:
        print(f"[FAIL] Final status verification failed: {e}")
        sys.exit(1)

    print("[SUCCESS] ALL END-TO-END ONBOARDING ASSESSMENT FLOW TESTS PASSED!")

if __name__ == "__main__":
    run_test()
