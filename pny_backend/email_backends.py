import base64
import os
import requests
from django.core.mail.backends.base import BaseEmailBackend

class ResendEmailBackend(BaseEmailBackend):
    """
    A custom Django email backend that sends emails using the Resend HTTP API.
    Bypasses SMTP port restrictions (like port 587 blocks on Railway/Render).
    """
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        api_key = os.getenv('RESEND_API_KEY')
        if not api_key:
            print("[PNY] Resend Email Backend Error: RESEND_API_KEY environment variable is not set.")
            return 0
            
        sent_count = 0
        for message in email_messages:
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare standard API payload
            payload = {
                "from": message.from_email,
                "to": message.to,
                "subject": message.subject,
                "text": message.body,
            }
            
            # Find and extract HTML alternative
            html_content = None
            for content, mimetype in getattr(message, 'alternatives', []):
                if mimetype == 'text/html':
                    html_content = content
                    break
            
            if html_content:
                payload["html"] = html_content
            
            # Extract and encode attachments in Base64
            attachments = []
            for attachment in message.attachments:
                # message.attachments elements are either a tuple/list: (filename, content, mimetype)
                # or a MIMEBase object. We handle standard django tuple attachments.
                if isinstance(attachment, tuple) and len(attachment) >= 2:
                    filename = attachment[0]
                    content = attachment[1]
                    
                    if isinstance(content, str):
                        content_bytes = content.encode('utf-8')
                    else:
                        content_bytes = content
                    
                    attachments.append({
                        "filename": filename,
                        "content": base64.b64encode(content_bytes).decode('utf-8')
                    })
            
            if attachments:
                payload["attachments"] = attachments
                
            try:
                response = requests.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                if response.status_code in [200, 201]:
                    sent_count += 1
                else:
                    err_msg = f"Resend API error response (Status {response.status_code}): {response.text}"
                    print(f"[PNY] {err_msg}")
                    if not self.fail_silently:
                        raise Exception(err_msg)
            except Exception as e:
                print(f"[PNY] Exception when calling Resend API: {str(e)}")
                if not self.fail_silently:
                    raise
                
        return sent_count
