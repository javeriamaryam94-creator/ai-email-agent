import os
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def check_and_reply_inbox():
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_password:
        print("Gmail credentials missing.")
        return

    print("Connecting to Gmail IMAP to check unread buyer replies...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_password)
        mail.select("inbox")

        # Search for unread emails
        status, messages = mail.search(None, '(UNSEEN)')
        if status != 'OK':
            print("No new messages found.")
            return

        for num in messages[0].split():
            res, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["Subject"]
                    sender = msg["From"]
                    
                    # Extract body text
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                    print(f"New reply from {sender} | Subject: {subject}")

                    # Generate AI response using Gemini
                    prompt = f"""
                    You are an expert B2B Export Manager for 'Indus Export Hub' (Himalayan Pink Salt & organic spices).
                    A prospective buyer replied to our cold outreach:
                    - Sender: {sender}
                    - Subject: {subject}
                    - Message: {body}
                    
                    Write a professional, formal, helpful B2B reply addressing their inquiries (such as MOQ, FOB/CIF pricing, or quality certificates like ISO/HACCP/Halal). Keep it concise and executive-level.
                    Return ONLY the reply email body text.
                    """
                    
                    response = model.generate_content(prompt)
                    ai_reply_text = response.text.strip()

                    # Send the automated reply back via SMTP
                    msg_reply = MIMEText(ai_reply_text)
                    msg_reply['Subject'] = f"Re: {subject}"
                    msg_reply['From'] = gmail_user
                    msg_reply['To'] = sender

                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(gmail_user, gmail_password)
                    server.sendmail(gmail_user, sender, msg_reply.as_string())
                    server.quit()
                    print(f"Successfully sent automated AI reply to {sender}")

        mail.logout()
    except Exception as e:
        print(f"Error checking replies: {e}")

if __name__ == "__main__":
    check_and_reply_inbox()
