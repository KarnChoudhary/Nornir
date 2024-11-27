import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Chrome options to disable notifications
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")

# Set up the Selenium WebDriver with Chrome options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL of the LMS login page
login_url = 'https://learn.soic.in/learn/account/signin'

# Open the login page
driver.get(login_url)
logging.info("Opened the login page")

# Wait for the page to load completely
time.sleep(5)  # Adjust the sleep time as needed

# Directly fill in the email and password fields
email_field = driver.find_element(By.NAME, 'Email*')
password_field = driver.find_element(By.NAME, 'Password*')

email_field.send_keys('market.karnchoudhary@gmail.com')
password_field.send_keys('bsnlcdr@123')
logging.info("Filled in the email and password fields")

# Wait for the sign-in button to become clickable
wait = WebDriverWait(driver, 60)  # Increase the wait time to 60 seconds

# Use the correct selector for the sign-in button
login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-1dqdd2d')))

# Scroll the button into view
driver.execute_script("arguments[0].scrollIntoView(true);", login_button)

# Ensure the button is enabled
if login_button.is_enabled():
    login_button.click()
    logging.info("Clicked the sign-in button")
else:
    logging.error("Sign-in button is not enabled")

# Wait for the login to complete
time.sleep(5)  # Adjust the sleep time as needed

# Pause for manual CAPTCHA solving
input("Press Enter after solving the CAPTCHA...")
logging.info("Manual CAPTCHA solved")

# Navigate to the page containing questions and answers
questions_url = 'https://learn.soic.in/learn/home/SOIC-Course/SOIC-Intensive-Course-English/section/302460/lesson/1889591'
driver.get(questions_url)
logging.info("Navigated to the questions page")

# Wait for the content to load
driver.implicitly_wait(10)

# Pause for manual scrolling
input("Press Enter after finishing manual scrolling...")
logging.info("Manual scrolling complete")

# Open the CSV file for writing
with open('questions.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Question'])

    # Refresh the list of questions to handle stale elements
    question_elements = driver.find_elements(By.ID, 'react-mathjax-preview-result')
    questions_set = set()

    for question_element in question_elements:
        try:
            question_text = question_element.text.strip()
            if question_text and question_text not in questions_set:
                questions_set.add(question_text)
                logging.info(f"Added question: {question_text}")
                writer.writerow([question_text])
        except Exception as e:
            logging.warning(f"Failed to add question to the CSV: {e}")

logging.info("Questions saved to questions.csv")

# Close the WebDriver
driver.quit()
logging.info("WebDriver closed")
