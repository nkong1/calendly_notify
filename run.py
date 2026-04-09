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
    count = len(slots)
    first = slots[0]
    last = slots[-1]
    
    # Detailed body text
    body = (
        f"Great news! We found {count} available slots.\n"
        f"Earliest: {first}\n"
        f"Latest: {last}\n\n"
        "Full list of times:\n" + "\n".join(slots) +
        f"\n\nBook here: {get_current_month_url()}"
    )

    msg = MIMEText(body)
    # Dynamic Subject line so you know exactly what's up before opening the email
    msg["Subject"] = f"🚨 {count} Slots Available ({first} - {last})"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def get_slots(page):
    slots = []

    # Find only days that have availability
    available_days = page.query_selector_all("button[aria-label*='Times available']")

    for day in available_days:
        day_label = day.get_attribute("aria-label").replace(" - Times available", "")
        day.click()
        page.wait_for_timeout(1500)

        # Grab time buttons using the specific data-container attribute
        time_buttons = page.query_selector_all("button[data-container='time-button']")
        for t in time_buttons:
            time = t.get_attribute("data-start-time")
            if time:
                slots.append(f"{day_label} - {time}")

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