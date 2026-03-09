import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_approval_credentials_email(to_email: str, name: str, temp_password: str) -> bool:
    """
    Sends an HTML email with temporary login credentials.
    Reads SMTP settings from the app settings object.
    Returns True if successfully sent, False otherwise.
    """
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    print(f"[email_service] Sending to: {to_email}")
    print(f"[email_service] SMTP_USER: {smtp_user}")
    print(f"[email_service] SMTP_PASSWORD (first 4): {smtp_password[:4] if smtp_password else 'NOT SET'}...")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "SpacePoint Instructor Application Approved"
    msg["From"] = f"SpacePoint <{smtp_user}>"
    msg["To"] = to_email

    LOGO_URL = "https://spacepoint.ae/wp-content/uploads/2023/12/SpacePoint-Purple-Logo-e1766489433825-1024x261.png"

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:system-ui,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 0;background:#f3f4f6;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:16px;overflow:hidden;
                    box-shadow:0 4px 24px rgba(36,17,52,0.12);">

        <!-- Header with SpacePoint logo -->
        <tr>
          <td style="background:linear-gradient(135deg,#241134,#653f84);padding:28px 32px;">
            <img src="{LOGO_URL}" height="44" alt="SpacePoint" style="display:block;">
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 32px;">

            <h2 style="margin:0 0 6px 0;font-size:20px;font-weight:700;color:#1a1135;">
              Application Approved &#10003;
            </h2>
            <p style="margin:0 0 24px 0;font-size:12px;font-weight:700;color:#653f84;
                       text-transform:uppercase;letter-spacing:0.1em;">
              Instructor Scholarship Programme
            </p>

            <p style="margin:0 0 12px 0;font-size:15px;color:#374151;line-height:1.7;">
              Hello <strong>{name}</strong>,
            </p>
            <p style="margin:0 0 24px 0;font-size:15px;color:#374151;line-height:1.7;">
              Congratulations! Your
              <strong>SpacePoint Instructor Scholarship Application</strong>
              has been reviewed and
              <strong style="color:#653f84;">approved</strong>.
              You now have access to the SpacePoint Instructor Portal.
            </p>

            <!-- Credentials box -->
            <div style="background:#faf8ff;border:1px solid #ddd6fe;border-radius:12px;
                         padding:22px 26px;margin:0 0 24px 0;">
              <p style="margin:0 0 16px 0;font-size:11px;font-weight:700;
                         letter-spacing:0.18em;color:#653f84;text-transform:uppercase;">
                Your Login Credentials
              </p>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:8px 0;border-bottom:1px solid #ede9f7;">
                    <span style="font-size:11px;color:#9ca3af;text-transform:uppercase;
                                 letter-spacing:0.1em;">Email</span><br>
                    <span style="font-family:'Courier New',monospace;font-size:15px;
                                 color:#1a1135;font-weight:600;">{to_email}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 0 0 0;">
                    <span style="font-size:11px;color:#9ca3af;text-transform:uppercase;
                                 letter-spacing:0.1em;">Temporary Password</span><br>
                    <span style="font-family:'Courier New',monospace;font-size:20px;
                                 color:#653f84;font-weight:700;letter-spacing:0.05em;">{temp_password}</span>
                  </td>
                </tr>
              </table>
            </div>

            <!-- Warning note -->
            <div style="background:#fffbeb;border-left:4px solid #f59e0b;
                         border-radius:0 8px 8px 0;padding:14px 18px;margin:0 0 28px 0;">
              <p style="margin:0;font-size:13px;color:#92400e;line-height:1.6;">
                <strong>&#9888; Action Required:</strong>
                This is a temporary password. Please log in and set a personal
                password before accessing your instructor resources.
              </p>
            </div>

            <!-- CTA button -->
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:linear-gradient(135deg,#241134,#653f84);border-radius:10px;">
                  <a href="http://localhost:8000"
                     style="display:inline-block;padding:13px 32px;font-size:14px;
                            font-weight:700;color:#ffffff;text-decoration:none;letter-spacing:0.04em;">
                    Log In to Instructor Portal &rarr;
                  </a>
                </td>
              </tr>
            </table>

            <p style="margin:28px 0 0 0;font-size:14px;color:#6b7280;line-height:1.7;">
              Best regards,<br>
              <strong style="color:#241134;">The SpacePoint Team</strong>
            </p>

          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f9fafb;padding:18px 32px;border-top:1px solid #ede9f7;">
            <p style="margin:0;font-size:12px;color:#9ca3af;text-align:center;line-height:1.7;">
              &copy; 2026 SpacePoint &nbsp;&middot;&nbsp; www.spacepoint.ae<br>
              <em>Do not reply to this email. This mailbox is not monitored.</em>
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""

    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"[email_service] Email sent successfully to {to_email}")
        return True
    except Exception as e:
        import traceback
        print(f"[email_service] Failed to send email to {to_email}: {str(e)}")
        traceback.print_exc()
        return False
