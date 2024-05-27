# import sys
# import time
# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver import ActionChains
# from selenium.webdriver.support import expected_conditions as EC
# import pyautogui
# import os
# import time
# import sys
# import pygetwindow as gw
# import pyautogui
# import threading
# import pickle
# import traceback
# from google.cloud import storage
# import os
# import uuid
# import csv
# import sys
# import subprocess
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
import pyautogui
import os
import time
import sys
import pygetwindow as gw
import pyautogui
import threading
import pickle
from datetime import datetime, timedelta
import traceback
from google.cloud import storage
import os
import uuid
import csv
import sys


# driver = webdriver.Edge()

# driver.get("https://tracker.toptal.com/app/projects?tab=active&sort-by=project-name&sort-order=asc")


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# Setup WebDriver

def handle_popup():
    
    driver.refresh()
    try:
        ok_button_locator = (By.CSS_SELECTOR, ".button_container .btn.btn-primary.modal_primary_btn.close_action")

        # Wait for the "Ok" button to be clickable
        wait = WebDriverWait(driver, 3 ) # Wait up to 10 seconds
        ok_button = wait.until(EC.element_to_be_clickable(ok_button_locator))
        ok_button.click()
    except:
        pass

    try:
        # Wait for the popup to appear, but only for a short period
        popup_ok_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.message_container .btn.btn-primary.modal_primary_btn.close_action')))
        popup_ok_button.click()
        print("Popup handled.")
    except:
        # If the popup doesn't appear within the timeout, we just ignore it
        print("No First popup appeared.")
        
    try:
        # Wait for the success modal to appear, but only for a short period
        success_modal_close_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#success_modal .modal_primary_btn.close_action')))
        success_modal_close_button.click()
        print("Success modal handled.")
    except:
        # If the success modal doesn't appear within the timeout, we just ignore it
        print("No success modal appeared.")
        
    try:
        # Wait for the success modal to appear, but only for a short period
        success_modal_close_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#error_modal .modal_primary_btn.close_action')))
        success_modal_close_button.click()
        print("Success modal handled.")
    except:
        # If the success modal doesn't appear within the timeout, we just ignore it
        print("No Error modal appeared.")
        
        
driver = webdriver.Edge()

# Navigate to the page with the form

# Initialize WebDriverWait
wait = WebDriverWait(driver, 10) # wait for a maximum of 10 seconds

 # Open the target webpage
driver.get("https://internshala.com/")



try:
    WebDriverWait(driver, 3).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.internship"))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.internship")
except:
    
    try:
        handle_popup()
    except:
        pass
    wait = WebDriverWait(driver, 2)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'internship_container')))

    labels = driver.find_elements(By.XPATH, "//label[contains(text(), 'I am still processing the applications and have not finished hiring yet')]")
    # labels = driver.find_elements(By.XPATH, "//label[contains(text(), 'I am still processing the applications and have not finished hiring yet')]")
    time.sleep(2)
    for label in labels:
        # Get the 'for' attribute to find the associated radio button
        radio_button_id = label.get_attribute('for')
        radio_button = driver.find_element(By.ID, radio_button_id)
        # Use JavaScript to click the radio button
        driver.execute_script("arguments[0].click();", radio_button)
        
        
    submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'submit_button')))

    # Click the submit button
    submit_button.click()
    
    try:
        handle_popup()
    except:
        pass
    
    driver.get("https://internshala.com/")
    time.sleep(2)




# Wait and click the hamburger menu
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "hamburger_menu_key"))
).click()

# Wait and click the "Login" button in the menu
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".home_page_login_button"))
).click()

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