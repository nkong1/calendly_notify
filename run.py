import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from playwright.sync_api import sync_playwright
import os

EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECEIVER = os.environ["EMAIL_RECEIVER"]

def get_current_month_url():
    month = datetime.now().strftime("%Y-%m")
    return f"https://calendly.com/kong_nicholas-berkeley/30min?month={month}"
    return f"https://calendly.com/leantutor-berkeley/leantutor-user-study?month={month}"

def send_email(slots):
    msg = MIMEText("Calendly slots are available — book now!\n\n" + "\n".join(slots))
    msg["Subject"] = "🚨 Calendly Slot Available!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def get_slots(page):
    buttons = page.query_selector_all("button")
    slots = []
    for b in buttons:
        text = b.inner_text().strip()
        if any(x in text.lower() for x in ["am", "pm"]):
            slots.append(text)
    return sorted(set(slots))

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(get_current_month_url())
        page.wait_for_selector("button")
        page.wait_for_timeout(3000)

        slots = get_slots(page)
        if slots:
            print("Slots found, sending email:", slots)
            send_email(slots)
        else:
            print("No slots available.")

if __name__ == "__main__":
    main()