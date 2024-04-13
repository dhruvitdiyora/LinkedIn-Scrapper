import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle

# Initialize Chrome options
chrome_options = Options()
today = datetime.today().strftime('%Y-%m-%d')
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('LINKEDIN_USERNAME')
password = os.getenv('LINKEDIN_PASSWORD')
#LinkedIn Credentials

# Set LinkedIn page URL for scraping
page = 'https://www.linkedin.com/company/nike'

# Initialize WebDriver for Chrome
browser = webdriver.Chrome()

# Open LinkedIn login page
browser.get('https://www.linkedin.com/login')

# Enter login credentials and submit
elementID = browser.find_element(By.ID, "username")
elementID.send_keys(username)
elementID = browser.find_element(By.ID, "password")
elementID.send_keys(password)
elementID.submit()


post_page = page + '/posts'
post_page = post_page.replace('//posts','/posts')
browser.get(post_page)

# Extract company name from URL
company_name = page.rstrip('/').split('/')[-1].replace('-',' ').title()
print(company_name)

# Set parameters for scrolling through the page
SCROLL_PAUSE_TIME = 1.5
MAX_SCROLLS = 25
last_height = browser.execute_script("return document.body.scrollHeight")
scrolls = 0
no_change_count = 0

while True:
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = browser.execute_script("return document.body.scrollHeight")
    no_change_count = no_change_count + 1 if new_height == last_height else 0
    if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
        break
    last_height = new_height
    scrolls += 1

pickle.dump(browser.get_cookies(), open("cookies.pkl","wb"))
# Parse the page source with BeautifulSoup
company_page = browser.page_source
linkedin_soup = bs(company_page.encode("utf-8"), "html.parser")
