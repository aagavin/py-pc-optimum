import argparse
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getenv
from pathlib import Path

import img2pdf
from playwright.sync_api import sync_playwright

SCREENSHOT_PATH = "shoot.png"
SMTP_SERVER: str = getenv("SMTP_SERVER", "")
PORT: int = int(getenv("SMTP_PORT", 0))  # For starttls
SENDER_EMAIL: str = getenv("E_USERNAME", "")
PASSWORD: str = getenv("E_PASSWORD", "")


def take_screenshot(username: str, password: str):
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page(viewport={"width": 750, "height": 800})

        # Login
        page.goto("https://www.pcoptimum.ca/login")
        page.fill("input#email", username)
        page.fill("input#password", password)

        with page.expect_navigation():
            page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # remove uneeded elements
        page.evaluate(
            """
            () => {
              document.querySelector('footer.site-footer')?.remove();
              document.querySelector('section.checklist-container')?.remove()
              document.querySelector('nav.menu')?.remove()
            }
            """
        )
        page.screenshot(full_page=True, path=SCREENSHOT_PATH, type="png")
        browser.close()


def send_email():
    text = f"PC POINTS FOR {parser.parse_args().username}"
    message = MIMEMultipart("alternative")
    message["Subject"] = text
    message["From"] = SENDER_EMAIL
    message["To"] = SENDER_EMAIL
    with open(SCREENSHOT_PATH, "rb") as attachment:
        attach_part = MIMEApplication(img2pdf.convert(attachment))
        attach_part.add_header(
            "Content-Disposition",
            "attachment",
            filename=SCREENSHOT_PATH.replace(".jpg", ".pdf"),
        )

    text_part = MIMEText(text, "plain")

    message.attach(text_part)
    message.attach(attach_part)

    with smtplib.SMTP(host=SMTP_SERVER, port=PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, message.as_string())


def main(username: str, password: str):
    take_screenshot(username, password)
    send_email()
    # remove file
    Path(SCREENSHOT_PATH).unlink(missing_ok=True)


# args
parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
args = parser.parse_args()
main(args.username, args.password)
