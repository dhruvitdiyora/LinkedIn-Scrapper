# bot to scrap jobs page from linkedin


import os
import sys
import pickle
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

except (ModuleNotFoundError, ImportError):
    print("selenium module not found")
    os.system(f"{sys.executable} -m pip install -U selenium")
finally:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


page = 'https://www.linkedin.com/jobs/collections/recommended/'

options = Options()

CHROMEDRIVER_PATH = "C:/chromedriver/chromedriver.exe"


CHROME_USER_DIR = "C:/Users/dhruv/AppData/Local/Google/Chrome/User Data"
options.add_argument("--user-data-dir=C:/Users/dhruv/AppData/Local/Google/Chrome/User Data/Default")


options.add_argument("--profile-directory=Default")
options.add_argument("--disable-extensions")
# options.add_argument("--disable-proxy-certificate-handler")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-gpu")



browser = webdriver.Chrome(options)
cookies = pickle.load(open("cookies.pkl", "rb"))
browser.get(page)
for cookie in cookies:
    browser.add_cookie(cookie)



# SCROLL_PAUSE_TIME = 1.5
# MAX_SCROLLS = 5
# last_height = browser.execute_script("return document.body.scrollHeight")
# scrolls = 0
# no_change_count = 0

# while True:
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(SCROLL_PAUSE_TIME)
#     new_height = browser.execute_script("return document.body.scrollHeight")
#     no_change_count = no_change_count + 1 if new_height == last_height else 0
#     if no_change_count >= 2 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
#         break
#     last_height = new_height
#     scrolls += 1

header = browser.find_element(By.CSS_SELECTOR, ".jobs-search-results-list__header")
scroll_origin = ScrollOrigin.from_element(header, 50, 100) # Offset: right/down
for i in range(5):
    ActionChains(browser).scroll_from_origin(scroll_origin, 0, 1000).perform() # Scroll down
    time.sleep(1)

page = browser.page_source
linkedin_soup = bs(page.encode("utf-8"), "html.parser")
jobs = []
containers = [container for container in linkedin_soup.find_all("div",{"class":"job-card-container"})]
for position in containers:
        promoted = position.find_element(By.CSS_SELECTOR, ".job-card-container__footer-item").text
        if promoted == "Promoted":
            continue

        company = position.find_element(By.CSS_SELECTOR, ".job-card-container__primary-description").text
        link = position.find_element(By.CSS_SELECTOR, "a.job-card-list__title").get_attribute('href').split('?eBP')[0]
        title = position.find_element(By.CSS_SELECTOR, "a.job-card-list__title").text
        picture = position.find_element(By.CSS_SELECTOR, "img.ember-view").get_attribute('src')
        jobs.append((company, title, link, picture))

jobs = []

print("hello")

# get elements if there is paging to go to next page
pagination_indicators= browser.find_elements(By.CLASS_NAME, "artdeco-pagination__indicator.artdeco-pagination__indicator--number")

selected_element = None
for indicator in pagination_indicators:
    if "selected" in indicator.get_attribute("class"):
        selected_element = indicator
        break

# Click the next pagination element
if selected_element and selected_element.find_element(By.XPATH, "./following-sibling::li"):
    next_element = selected_element.find_element(By.XPATH, "./following-sibling::li")
    next_element.click()

# Wait for the page to load and close the browser
wait = WebDriverWait(browser, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "artdeco-pagination__indicator.artdeco-pagination__indicator--number")))


print("hello")
