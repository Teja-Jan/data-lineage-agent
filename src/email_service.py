import os
import smtplib
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId
)

def send_impact_report(recipient_email, attachment_data, attachment_filename):
    """
    Sends the generated XLSX impact report via the configured EMAIL_PROVIDER.
    Supports 'SENDGRID' (via API) or 'SMTP' (via smtplib).
    """
    provider = os.getenv("EMAIL_PROVIDER", "SENDGRID").upper()
    
    if provider == "SENDGRID":
        return _send_via_sendgrid(recipient_email, attachment_data, attachment_filename)
    elif provider == "SMTP":
        return _send_via_smtp(recipient_email, attachment_data, attachment_filename)
    else:
        return False, f"Configuration Error: Unsupported EMAIL_PROVIDER '{provider}'. Must be SENDGRID or SMTP."

def _send_via_sendgrid(recipient_email, attachment_data, attachment_filename):
    sg_api_key = os.getenv("SENDGRID_API_KEY", "")
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "alerts@enterpriselineage.com")
    
    if not sg_api_key or sg_api_key == "YOUR_SENDGRID_KEY_HERE":
        return False, "SendGrid API Key is not configured in .env."

    subject = f"Impact Analysis Report: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    body_text = f"""
    The following Enterprise Data Lineage and Impact Intelligent Analysis report has been generated for your review.
    
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Impact Scope: Automated Assessment of Downstream Dependencies.
    
    Please find the attached {attachment_filename} for full details.
    """

    message = Mail(
        from_email=from_email,
        to_emails=recipient_email,
        subject=subject,
        plain_text_content=body_text
    )

    if attachment_data:
        encoded_file = base64.b64encode(attachment_data).decode()
        
        attachment = Attachment()
        attachment.file_content = FileContent(encoded_file)
        attachment.file_type = FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        attachment.file_name = FileName(attachment_filename)
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Ecosystem_Impact_Report')
        
        message.attachment = attachment

    try:
        sg = SendGridAPIClient(sg_api_key)
        response = sg.send(message)
        if response.status_code in [200, 201, 202]:
            return True, f"Email successfully queued via SendGrid (Status: {response.status_code})."
        else:
            return False, f"SendGrid API Error (Status: {response.status_code})"
    except Exception as e:
        return False, f"SendGrid Exception: {str(e)}"

def _send_via_smtp(recipient_email, attachment_data, attachment_filename):
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    
    msg = MIMEMultipart()
    msg['Subject'] = f"📊 Impact Analysis Report: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['From'] = "alerts@enterpriselineage.com"
    msg['To'] = recipient_email
    
    body = f"""
    The following Enterprise Data Lineage and Impact Intelligent Analysis report has been generated for your review.
    
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Impact Scope: Automated Assessment of Downstream Dependencies.
    
    Please find the attached {attachment_filename} for full details.
    """
    msg.attach(MIMEText(body, 'plain'))
    
    if attachment_data:
        part = MIMEApplication(attachment_data, Name=attachment_filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)
    
    try:
        if smtp_user and smtp_pass:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(msg)
        return True, "Email successfully dispatched via SMTP Server."
    except Exception as e:
        return False, f"SMTP Exception: {str(e)}"
