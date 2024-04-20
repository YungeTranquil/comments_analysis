import os
import sys
import time
import json
import requests
import yaml
import re

import numpy as np
import pandas as pd
from tqdm import tqdm
import json

from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
def start_browser(headless=False):
    options = Options()
    if headless == True:
        options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    #options.add_argument('--disable-extensions')
    #options.add_argument('--disable-infobars')
    #options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--no-sandbox')
    #options.add_argument('--disable-popup-blocking')
    #options.add_argument('--disable-default-apps')
    #options.add_argument('--disable-translate')
    #options.add_argument('--disable-web-security')
    #options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    #options.add_argument('--blink-settings=imagesEnabled=false')
    #options.add_argument('--disable-javascript')
    
    browser = webdriver.Chrome(options=options)

    browser.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
    #browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #  "source": """
    #    Object.defineProperty(navigator, 'webdriver', {
    #      get: () => undefined
    #    })
    #  """
    #})
    #browser.execute_cdp_cmd("Network.enable", {})
    #browser.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
    return browser

def start_headless_browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-javascript')
    
    browser = webdriver.Chrome(options=options)

    browser.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
    #browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #  "source": """
    #    Object.defineProperty(navigator, 'webdriver', {
    #      get: () => undefined
    #    })
    #  """
    #})
    #browser.execute_cdp_cmd("Network.enable", {})
    #browser.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
    return browser

def query_comments(url):
    browser.get(url)
    for element in browser.find_elements(By.CSS_SELECTOR,"div"):
        if element.get_attribute("role") == "combobox":
            language_box = element
    language_box.find_elements(By.CSS_SELECTOR,"div")[0].click()
    language_box.click()
    time.sleep(0.5)
    for element in browser.find_elements(By.CSS_SELECTOR,"ul"):
        if (element.get_attribute("aria-label") == "语言")|(element.get_attribute("aria-label") == "Language"):
            language_box = element
    language_box.find_elements(By.CSS_SELECTOR,"li")[-1].click()

def next_page_comments():
    span_elements = browser.find_elements(By.CSS_SELECTOR,"span")
    span_elements.reverse()
    for span in span_elements:
        if (span.text == "加载更多")|(span.text == "Load more"):
            next_page = span
            break
    next_page.click()

def parse_comments(path=None):
    if path != None:
        with open(f"{path}","r",encoding="utf-8") as file:
            response = file.read()
    else:
        response = browser.page_source
    
    response = BeautifulSoup(response)

    # 从浏览器获取标题和评论css id
    class_list = [section.get_attribute("class") for section in browser.find_elements(By.CSS_SELECTOR,"section")]
    header_class,comment_class = class_list[0],class_list[-1]
    info = browser.find_element(By.CSS_SELECTOR,f"section.{header_class}").text.split("\n")
    
    results = []
    
    response_list = response.find_all("section",attrs={"class":f"{comment_class}"})
    length = len(response_list)
    
    for i in tqdm(range(length)):
        try:
            rate = response_list[i].find("div",attrs={"class":"B1UG8d"}).attrs["title"]
            user = response_list[i].find("span").text
            comment = response_list[i].find("p").text
            comment_time = response_list[i].find("span",attrs={"class":"ydlbEf"}).text
            helpful_num = response_list[i].find("span",attrs={"class":"ZRk0Tb"}).text
            result = {"rate":rate, "user":user, "comment":comment, "comment_time":comment_time, "helpful":helpful_num}
            results.append(result)
        except:
            continue
    
    comment_output = pd.DataFrame(results)
    try:
        comment_output["comment_time"] = pd.to_datetime(comment_output["comment_time"],format="%Y年%m月%d日")
    except:
        try:
            comment_output["comment_time"] = pd.to_datetime(comment_output["comment_time"], format='%b %d, %Y')
        except:
            pass
    return comment_output

def check_browser(browser):
    time_now = pd.Timestamp.now().strftime(format="%m-%d-%H-%M")
    browser.save_screenshot(f"log/excptions/{time_now}.png")
    with open(f"log/excptions/{time_now}.html","w",encoding="utf-8") as file:
        file.write(browser.page_source)

def fetchUrl(url,cookies=None):
    """
    Fetches content from a URL using a GET request with custom User-Agent and cookies.
    """
    # Ensure headers and cookies are dictionaries, if not provided, initialize as empty dicts
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": user_agent}
    if cookies is None:
        cookies = {}
    
    # Perform the GET request
    response = requests.get(url, headers=headers, cookies=cookies)
    
    return response

def amazon_cookie_manage(country=None):
    """save cookie from https://moz.com/domain-analysis"""
    if country == None:
        with open("config/amazon_cookie.json","r") as file:
            cookies = json.loads(file.read())
            cookies = cookies["cookies"]
            cookies_amazon = {cookie["name"]:cookie["value"] for cookie in cookies}
    else:
        with open(f"config/amazon_cookie_{country}.json","r") as file:
            cookies = json.loads(file.read())
            cookies = cookies["cookies"]
            cookies_amazon = {cookie["name"]:cookie["value"] for cookie in cookies}


    return cookies_amazon

def sleep_time(base,random=1):
    random_time = base + np.random.randint(10000,99999)/(10**5)
    time.sleep(random_time)

def scroll_down_amazon(browser):
    points = np.random.randint(0,1080,10)
    points.sort()
    points = list(points)
    points.append(1280)
    timer = 0
    for location in points:
        browser.execute_script(f"window.scrollTo(0, {location})")
        time.sleep(0.1)
        timer += 1
        if timer%5 == 0:
            time.sleep(1)

if __name__ == "__main__":
    with open("data/black_list.json","r") as file:
        black_list = json.loads(file.read())

    country = sys.argv[1]
    input_data = pd.read_csv(f"data/amazon_semrush_{country}_2403.csv")
    url_list = input_data["URL"].to_list()

    start_index = int(sys.argv[2])
    counts = int(sys.argv[3])
    end_index = start_index + counts
    i = start_index
    
    if sys.argv[4] == "selenium":
        browser = start_browser()

        browser.get("https://www.amazon.com")

        for url in tqdm(url_list[start_index:end_index]):
            try:
                url = url+"?language=en_US"
                browser.get(url)
                sleep_time(1)
                scroll_down_amazon(browser)
                response = browser.page_source
                with open(f"data/amazon_html/{country}/amazon_{i}.html","w",encoding="utf-8") as file:
                    file.write(response)
                sleep_time(5)
                i += 1
            except:
                i += 1
                continue
    else:

        for url in tqdm(url_list[start_index:end_index]):

            if re.findall(r"/.+/dp",url)[0][1:-3] in black_list:
                i += 1
                continue

            if os.path.exists(f"data/amazon_html/{country}/amazon_{i}.html"):
                i += 1
                continue
            url = url+"?language=en_US"
            sleep_time(1)
            cookies = amazon_cookie_manage(country=country)
            response = fetchUrl(f"{url}",cookies=cookies)
            with open(f"data/amazon_html/{country}/amazon_{i}.html","w",encoding="utf-8") as file:
                file.write(response.text)
            sleep_time(5)
            i += 1