import json
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getenv
from pathlib import Path

import img2pdf
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

SCREENSHOT_PATH = ".jpg"
SMTP_SERVER: str = getenv("SMTP_SERVER", "")
PORT: int = int(getenv("SMTP_PORT", 0))  # For starttls
SENDER_EMAIL: str = getenv("E_USERNAME", "")
TO_EMAIL: str = getenv("E_TO", "")
PASSWORD: str = getenv("E_PASSWORD", "")


def take_screenshot(username: str, password: str):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({'width': 1366, 'height': 768})
        stealth_sync(page)

        try:
            # Go to login page
            page.goto("https://www.pcoptimum.ca", wait_until="networkidle")
            page.locator("ul.menu-desktop__list:nth-child(3) > li:nth-child(1) > a:nth-child(1) > span:nth-child(1)").click()

            # at login page fill user/pass
            page.fill("input#email", username)
            page.fill("input#password", password)

            page.click('button[type="submit"]')

            page.wait_for_selector('#end-navigation')
            page.locator("ul.menu-desktop__list:nth-child(2) > li:nth-child(2) > a:nth-child(1)").click()
            page.wait_for_load_state("networkidle")

            # remove unneeded elements
            page.evaluate(
                """
            () => {
            document.querySelector('footer.site-footer')?.remove();
            document.querySelector('section.checklist-container')?.remove()
            document.querySelector('nav.menu')?.remove()
            }
            """)

            # set inner text of header
            page.locator("div.container").screenshot(path=f"{username}_{SCREENSHOT_PATH}", type="jpeg", quality=100)

        except Exception as e:
            page.locator("div.container").screenshot(path=f"{username}_{SCREENSHOT_PATH}", type="jpeg", quality=100)
            raise e
        finally:
            browser.close()


def send_email(screenshots: list):
    text = f"PC POINTS FOR {', '.join([s.replace('_.jpg', '') for s in screenshots])}"
    message = MIMEMultipart("alternative")
    message["Subject"] = text
    message["From"] = SENDER_EMAIL
    message["To"] = TO_EMAIL

    for path in screenshots:
        with open(path, "rb") as attachment:
            attach_part = MIMEApplication(img2pdf.convert(attachment))
            attach_part.add_header(
                "Content-Disposition",
                "attachment",
                filename=path.replace(".jpg", ".pdf"),
            )
        message.attach(attach_part)

    text_part = MIMEText(text, "plain")

    message.attach(text_part)

    with smtplib.SMTP(host=SMTP_SERVER, port=PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, TO_EMAIL, message.as_string())


def main():
    try:
        users = json.loads(getenv("USERS", ""))
        screenshots = []
        for user in users:
            screen_path = f"{user['username']}_{SCREENSHOT_PATH}"
            screenshots.append(screen_path)
            take_screenshot(user['username'], user['password'])
        
        send_email(screenshots)
        # remove file
        Path(SCREENSHOT_PATH).unlink(missing_ok=True)
    except Exception as e:
        message = MIMEMultipart()
        message["Subject"] = "Error"
        message["From"] = SENDER_EMAIL
        message["To"] = SENDER_EMAIL
        message.attach(MIMEText(f"Error\n{e=}", "plain"))
        with smtplib.SMTP(host=SMTP_SERVER, port=PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, message.as_string())
        raise e


main()
