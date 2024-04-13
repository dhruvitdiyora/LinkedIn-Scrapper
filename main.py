# scaffold-finite-scroll
#     scaffold-finite-scroll--infinite

# window.scrollTo({ left: 0, top: document.body.scrollHeight, behavior: "smooth" })

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
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


page = 'https://www.linkedin.com/feed/'

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



# Set parameters for scrolling through the page
SCROLL_PAUSE_TIME = 1.5
MAX_SCROLLS = 200
last_height = browser.execute_script("return document.body.scrollHeight")
scrolls = 0
no_change_count = 0
# browser.get(page)


while True:
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = browser.execute_script("return document.body.scrollHeight")
    no_change_count = no_change_count + 1 if new_height == last_height else 0
    if no_change_count >= 2 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
        break
    last_height = new_height
    scrolls += 1

# Parse the page source with BeautifulSoup
page = browser.page_source
linkedin_soup = bs(page.encode("utf-8"), "html.parser")

# Extract post containers from the HTML
containers = [container for container in linkedin_soup.find_all("div",{"class":"feed-shared-update-v2"}) if 'activity' in container.get('data-urn', '')]

# Helper functions for date and reaction conversions
def get_actual_date(date):
    today = datetime.today().strftime('%Y-%m-%d')
    current_year = datetime.today().strftime('%Y')
    
    def get_past_date(days=0, weeks=0, months=0, years=0):
        date_format = '%Y-%m-%d'
        dtObj = datetime.strptime(today, date_format)
        past_date = dtObj - relativedelta(days=days, weeks=weeks, months=months, years=years)
        past_date_str = past_date.strftime(date_format)
        return past_date_str

    past_date = date
    
    if 'hour' in date:
        past_date = today
    elif 'day' in date:
        date.split(" ")[0]
        past_date = get_past_date(days=int(date.split(" ")[0]))
    elif 'week' in date:
        past_date = get_past_date(weeks=int(date.split(" ")[0]))
    elif 'month' in date:
        past_date = get_past_date(months=int(date.split(" ")[0]))
    elif 'year' in date:
        past_date = get_past_date(months=int(date.split(" ")[0]))
    else:
        split_date = date.split("-")
        if len(split_date) == 2:
            past_month = split_date[0]
            past_day =  split_date[1]
            if len(past_month) < 2:
                past_month = "0"+past_month
            if len(past_day) < 2:
                past_day = "0"+past_day
            past_date = f"{current_year}-{past_month}-{past_day}"
        elif len(split_date) == 3:
            past_month = split_date[0]
            past_day =  split_date[1]
            past_year = split_date[2]
            if len(past_month) < 2:
                past_month = "0"+past_month
            if len(past_day) < 2:
                past_day = "0"+past_day
            past_date = f"{past_year}-{past_month}-{past_day}"

    return past_date



def convert_abbreviated_to_number(s):
    if 'K' in s:
        return int(float(s.replace('K', '')) * 1000)
    elif 'M' in s:
        return int(float(s.replace('M', '')) * 1000000)
    else:
        return int(s)



# Define a data structure to hold all the post information
posts_data = []

def get_text(container, selector, attributes):
    try:
        element = container.find(selector, attributes)
        if element:
            return element.text.strip()
    except Exception as e:
        print(e)
    return ""

def get_job_link(container, selector, attributes):
    try:
        element = container.find(selector, attributes)
        link = element.find_all('a')[0].get('href')
        if element:
            return link
    except Exception as e:
        print(e)
    return ""

# Function to extract media information
def get_media_info(container):
    media_info = [("div", {"class": "update-components-video"}, "Video"),
                  ("div", {"class": "update-components-linkedin-video"}, "Video"),
                  ("div", {"class": "update-components-image"}, "Image"),
                  ("article", {"class": "update-components-article"}, "Article"),
                  ("div", {"class": "feed-shared-external-video__meta"}, "Youtube Video"),
                  ("div", {"class": "feed-shared-mini-update-v2 feed-shared-update-v2__update-content-wrapper artdeco-card"}, "Shared Post"),
                  ("div", {"class": "feed-shared-poll ember-view"}, "Other: Poll, Shared Post, etc")]
    
    for selector, attrs, media_type in media_info:
        element = container.find(selector, attrs)
        if element:
            link = element.find('a', href=True)
            return link['href'] if link else "None", media_type
    return "None", "Unknown"


# Main loop to process each container
for container in containers:
    post_text = get_text(container, "div", {"class": "feed-shared-update-v2__description-wrapper"})
    media_link, media_type = get_media_info(container)
    post_job_link = None
    # get_job_link(container, "div", {"class": "update-components-entity__content-wrapper"})
    post_date = get_text(container, "div", {"class": "update-components-text-view break-words"})
    post_date = get_actual_date(post_date)
    profile = get_job_link(container, "div", {"class": "update-components-actor__container"})
    posts_data.append({"text":post_text,"date":post_date,"media_link":media_link,"link":post_job_link,"prof_link":profile})
  
 # Convert the data into a DataFrame and perform data cleaning and sorting
try:
    df = pd.DataFrame(posts_data)
    for col in df.columns:
        try:
            df[col] = df[col].astype(int)
        except ValueError:
            pass
except Exception as e:
    print(f"Error processing data: {e}")
       

# Export the DataFrame to a CSV file
csv_file = f"posts_"+datetime.now().strftime("%d_%m_%Y") + ".csv"
df.to_csv(csv_file, encoding='utf-8', index=False)
print(f"Data exported to {csv_file}")