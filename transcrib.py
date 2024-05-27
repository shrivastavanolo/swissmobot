from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
import time

##SELENIUM SCRIPT TO GET TRANSCRIPTION OF VID FROM LOOM WEBSITE
#NOT TO BE USED IN MAIN BOT FILE
#ALREADY BEING CALLED IN HELPER.PY SCRIPT

#XPATH OF 'TRANSCRIPTION' BUTTON ON LOOM WEBSITE
#MIGHT VARY ACCORDING TO BROWSER
t_x_path= '//*[@id="right-panel-tabs"]/div/nav/button[2]'

##XPATH OF 'COPY' BUTTON ON LOOM WEBSITE'S TRANSCRIPTION TAB
#MIGHT VARY ACCORDING TO BROWSER
copy_xpath = '//*[@id="activity-sidebar-container"]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[2]/button/span/div/span[2]'
  
def get_transcrib_from_loom(url):
  name=url.strip().split("/")[-1]
  driver = webdriver.Edge()
  driver.get(url)
  time.sleep(2)
  tran = driver.find_element(By.XPATH,t_x_path )

  try:
      # Use JavaScript to click the element
      driver.execute_script("arguments[0].click();", tran)
  except UnexpectedAlertPresentException:
      alert = driver.switch_to.alert
      alert.accept()  # Accept the alert
      time.sleep(1)  # Wait for the alert to be handled
      driver.execute_script("arguments[0].click();", tran)

  print('done1')
  time.sleep(2)

  cop = driver.find_element(By.XPATH,copy_xpath )

  try:
      # Use JavaScript to click the element
      driver.execute_script("arguments[0].click();", cop)
  except UnexpectedAlertPresentException:
      alert = driver.switch_to.alert
      alert.accept()  # Accept the alert
      time.sleep(1)  # Wait for the alert to be handled
      driver.execute_script("arguments[0].click();", cop)

  print('done2')
  driver.execute_script("window.open('');")
  driver.switch_to.window(driver.window_handles[1])
  driver.get('data:text/html,<html contenteditable>')  # Opens a blank editable page

  # Simulate paste action
  editable_body = driver.find_element(By.TAG_NAME, 'body')
  editable_body.send_keys(Keys.CONTROL, 'v')
  
  time.sleep(2)  # Wait to see the pasted content
  copied_content = editable_body.text
  print(f"Copied content: {copied_content}")

  # Save the copied content to a text file on the local system
  with open(f'{name}.txt', 'w') as file:
      file.write(copied_content)
  return f'{name}.txt'

#TRIAL

# get_transcrib_from_loom("https://www.loom.com/share/13b6cb2e76bf4051b49cc12ee8ffd8fe")
