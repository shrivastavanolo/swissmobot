import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import sys
import pygetwindow as gw
import pyautogui
import threading
import pickle
from datetime import datetime, timedelta
import traceback
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url="https://internshala.com/hire-talent"

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 10) # wait for a maximum of 10 seconds

driver.get(url)

# Wait and click the "Login" button in the menu
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="header_login_button"]'))).click()

# Wait for the login modal to appear and click on "Employer / T&P"
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "modal_employer"))
).click()

# Fill out the email and password fields
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "modal_email"))
).send_keys("Contact@SystemicAltruism.com")

WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "modal_password"))
).send_keys("vibevilla123")

# Click the login button
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "modal_login_submit"))
).click()


time.sleep(4)

# Remember to close the driver after your automation task is done
# driver.quit()

cookies = driver.get_cookies()
    
# Modify expiry date of each cookie (adding 30 days to each)
for cookie in cookies:
    if 'expiry' in cookie:
        print(cookie['expiry'])
        # Convert expiry timestamp to a datetime object
        expiry_date = datetime.fromtimestamp(cookie['expiry'])
        print("date", expiry_date)
        # Extend the expiry by 30 days
        new_expiry_date = expiry_date + timedelta(days=30)
        # Update the cookie's expiry timestamp
        cookie['expiry'] = int(new_expiry_date.timestamp())

# Save the modified cookies back to the pickle file
print(cookies)
pickle.dump(cookies, open(f"internshala_automation.pkl", "wb"))
# pickle.dump(, open("pimeyes_cookies.pkl", "wb"))

time.sleep(2)

with open("cookies_name_intern.txt", "w") as file:
    file.write(f"internshala_automation.pkl")
    
time.sleep(2)  