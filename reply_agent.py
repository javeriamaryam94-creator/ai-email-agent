import os
import time
import base64
from email.message import EmailMessage
from email.utils import parseaddr
import google.generativeai as genai
from gmail_auth import get_gmail_service

# Configure Gemini API (REST avoids gRPC stalls on Windows/Git Bash)
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is missing!")

genai.configure(api_key=os.environ["GEMINI_API_KEY"], transport="rest")
model = genai.GenerativeModel("gemini-3.8-flash")

SKIP_SENDERS = (
    "noreply",
    "no-reply",
    "notifications@",
    "mailer-daemon",
    "postmaster",
)


def get_header(message, name):
    return next(
        (
            header["value"]
            for header in message["payload"].get("headers", [])
            if header["name"].lower() == name.lower()
        ),
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

    return walk(payload) or message.get("snippet", "")


def generate_reply_with_retry(prompt, retries=5, timeout=30):
    last_err = None
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt, request_options={"timeout": timeout})
            text = (getattr(response, "text", "") or "").strip()
            if text:
                return text
            raise RuntimeError("Empty response from Gemini model.")
        except Exception as exc:
            last_err = exc
            msg = str(exc).lower()
            is_transient = (
                "503" in msg
                or "unavailable" in msg
                or "timeout" in msg
                or "timed out" in msg
                or "429" in msg
            )
            if not is_transient or attempt == retries - 1:
                raise
            sleep_s = min(2 ** attempt, 16)
            print(f"Transient Gemini error ({exc}); retrying in {sleep_s}s...")
            time.sleep(sleep_s)
    raise last_err


def should_skip_sender(sender_header):
    if os.environ.get("REPLY_ALL_UNREAD") == "1":
        return False
    _, addr = parseaddr(sender_header)
    target = (addr or sender_header).lower()
    return any(token in target for token in SKIP_SENDERS)


def send_threaded_reply(service, to_addr, subject, body, thread_id, message_id):
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if message_id:
        msg["In-Reply-To"] = message_id
        msg["References"] = message_id

    msg.set_content(body)
    raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    send_body = {"raw": raw_b64}
    if thread_id:
        send_body["threadId"] = thread_id

    return service.users().messages().send(userId="me", body=send_body).execute()


def check_and_reply_inbox():
    service = get_gmail_service()
    dry_run = os.environ.get("DRY_RUN") == "1"

    print("Checking Gmail for unread buyer replies...")
    results = (
        service.users()
        .messages()
        .list(userId="me", q="is:unread", maxResults=20)
        .execute()
    )
    messages = results.get("messages", [])
    if not messages:
        print("No unread messages found.")
        return

    for item in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="full")
            .execute()
        )
        sender = get_header(msg, "From")
        subject = get_header(msg, "Subject") or "(No Subject)"
        rfc_msg_id = get_header(msg, "Message-ID")
        thread_id = msg.get("threadId")
        body_text = get_plain_text(msg)

        print(f"New reply from {sender} | Subject: {subject}")

        if should_skip_sender(sender):
            print(f"Skipping automated/notification sender: {sender}")
            continue

        prompt = (
            "You are a helpful sales and export assistant replying to an email. "
            "Write a clear, polite, concise reply addressing the sender's message.\n\n"
            f"From: {sender}\n"
            f"Subject: {subject}\n"
            f"Message:\n{body_text[:4000]}"
        )

        reply_text = generate_reply_with_retry(prompt)

        if dry_run:
            print(f"[DRY RUN] Would reply to {sender}:\n{reply_text}\n")
            continue

        send_threaded_reply(
            service=service,
            to_addr=sender,
            subject=subject,
            body=reply_text,
            thread_id=thread_id,
            message_id=rfc_msg_id,
        )
        service.users().messages().modify(
            userId="me",
            id=item["id"],
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()
        print(f"Successfully sent threaded Gmail API reply to {sender}")


if __name__ == "__main__":
    try:
        check_and_reply_inbox()
    except Exception as e:
        print(f"Error checking replies: {e}")
