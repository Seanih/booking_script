# Selenium used to automate browser tasks
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from twilio.rest import Client
from dotenv import load_dotenv
import os
import yagmail

# Load environment variables from .env file
load_dotenv()


def get_driver():
    # set options for driver to make scraping easier
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options)
    # fetch data from endpoint
    driver.get("https://katalon-demo-cura.herokuapp.com/")
    return driver


def send_email(details_obj):
    sender = os.getenv("FROM_EMAIL")
    receiver = os.getenv("TO_EMAIL")

    subject = "Cura Healthcare Appointment"

    content = f"""
    Cura Healthcare Appointment Confirmation Details:
    location: {details_obj['facility']}
    readmission: {details_obj['readmission']}
    program: {details_obj['program']}
    date: {details_obj['visit_date']}
    comments: {details_obj['comment']}
    """
    # get env variable
    gmail_app_pw = os.getenv("APP_PW")
    yag = yagmail.SMTP(user=sender, password=gmail_app_pw)

    # send multiple emails over a period of time
    yag.send(to=receiver, subject=subject, contents=content)
    print("sent confirmation email")


def send_text(details_obj):
    # Twilio credentials
    account_sid = os.getenv("ACCOUNT_SID")
    auth_token = os.getenv("AUTH_TOKEN")

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    content = f"""
    Cura Healthcare Appointment Confirmation Details:
    location: {details_obj['facility']}
    readmission: {details_obj['readmission']}
    program: {details_obj['program']}
    date: {details_obj['visit_date']}
    comments: {details_obj['comment']}
    """

    message = client.messages.create(
        from_="+18336973859", body=content, to="+18777804236"
    )

    print("Message sent after booking:\n", message.sid)


def main():
    # navigate to login page and log in
    driver = get_driver()
    driver.find_element(by="id", value="btn-make-appointment").click()
    driver.find_element(by="id", value="txt-username").send_keys("John Doe")
    driver.find_element(by="id", value="txt-password").send_keys(
        "ThisIsNotAPassword" + Keys.RETURN
    )

    # Locate the dropdown element and select option
    dropdown = driver.find_element(
        by="xpath", value="/html/body/section/div/div/form/div[1]/div/select"
    )
    select = Select(dropdown)
    select.select_by_value("Hongkong CURA Healthcare Center")

    # checkbox and radio button
    driver.find_element(by="id", value="chk_hospotal_readmission").click()
    driver.find_element(by="id", value="radio_program_none").click()

    # enter appointment date
    driver.find_element(by="id", value="txt_visit_date").send_keys("04/22/2024")

    # add comments
    driver.find_element(by="id", value="txt_comment").send_keys(
        "my stomach feels weird..."
    )

    # book appointment and get confirmation details
    driver.find_element(
        by="xpath", value="/html/body/section/div/div/form/div[6]/div/button"
    ).click()

    confirmation_details = {
        "facility": driver.find_element(by="id", value="facility").text,
        "readmission": driver.find_element(by="id", value="hospital_readmission").text,
        "program": driver.find_element(by="id", value="program").text,
        "visit_date": driver.find_element(by="id", value="visit_date").text,
        "comment": driver.find_element(by="id", value="comment").text,
    }

    # send confirmation email/text
    send_email(confirmation_details)
    send_text(confirmation_details)


if __name__ == "__main__":
    main()
