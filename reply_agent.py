import os
import base64
from email.message import EmailMessage
from email.utils import parseaddr

import google.generativeai as genai

from gmail_auth import get_gmail_service


# Configure Gemini API
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is missing!")

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


def get_header(message, name):
    return next(
        (header["value"] for header in message["payload"].get("headers", [])
         if header["name"].lower() == name.lower()),
        "",
    )


def get_plain_text(message):
    payload = message["payload"]

    def walk(part):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
        for child in part.get("parts", []):
            text = walk(child)
            if text:
                return text
        return ""

    return walk(payload)


def check_and_reply_inbox():
    service = get_gmail_service()
    gmail_user = service.users().getProfile(userId="me").execute()["emailAddress"]

    print("Checking Gmail for unread buyer replies...")
    try:
        result = service.users().messages().list(
            userId="me", q="is:unread", maxResults=20
        ).execute()

        for summary in result.get("messages", []):
            message_id = summary["id"]
            message = service.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()

            subject = get_header(message, "Subject")
            sender_header = get_header(message, "From")
            sender = parseaddr(sender_header)[1]
            original_message_id = get_header(message, "Message-ID")
            thread_id = message["threadId"]
            body = get_plain_text(message)

            print(f"New reply from {sender} | Subject: {subject}")

            prompt = f"""
            You are an expert B2B Export Manager for 'Indus Export Hub'
            (Himalayan Pink Salt & organic spices).
            A prospective buyer replied to our cold outreach:
            - Sender: {sender}
            - Subject: {subject}
            - Message: {body}

            Write a professional, formal, helpful B2B reply addressing their
            inquiries (such as MOQ, FOB/CIF pricing, or quality certificates
            like ISO/HACCP/Halal). Keep it concise and executive-level.
            Return ONLY the reply email body text.
            """

            ai_reply_text = model.generate_content(prompt).text.strip()

            reply = EmailMessage()
            reply["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
            reply["From"] = gmail_user
            reply["To"] = sender
            if original_message_id:
                reply["In-Reply-To"] = original_message_id
                reply["References"] = original_message_id
            reply.set_content(ai_reply_text)

            raw_message = base64.urlsafe_b64encode(reply.as_bytes()).decode("utf-8")
            service.users().messages().send(
                userId="me",
                body={"raw": raw_message, "threadId": thread_id},
            ).execute()

            service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()

            print(f"Successfully sent threaded Gmail API reply to {sender}")

    except Exception as error:
        print(f"Error checking replies: {error}")


if __name__ == "__main__":
    check_and_reply_inbox()
